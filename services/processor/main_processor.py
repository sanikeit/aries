#!/usr/bin/env python3

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject, GLib
import sys
import os
import json
import logging
import threading
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add DeepStream Python bindings to path
sys.path.append('/opt/nvidia/deepstream/deepstream/lib')

try:
    import pyds
except ImportError:
    logger.error("pyds module not found. Make sure DeepStream is properly installed.")
    sys.exit(1)

from services.pulsar_service import PulsarService
from services.config_service import ConfigService

class DeepStreamPipeline:
    """DeepStream pipeline for multi-camera video analytics"""
    
    def __init__(self):
        self.pipeline = None
        self.loop = None
        self.pulsar_service = PulsarService()
        self.config_service = ConfigService()
        self.running = False
        self.frame_count = 0
        
    def create_pipeline(self, config: Dict[str, Any]) -> bool:
        """Create the DeepStream pipeline with hardware acceleration"""
        try:
            # Initialize GStreamer
            Gst.init(None)
            
            # Create pipeline
            self.pipeline = Gst.Pipeline()
            if not self.pipeline:
                logger.error("Failed to create pipeline")
                return False
            
            # Create elements
            self._create_elements(config)
            
            # Add elements to pipeline
            self._add_elements_to_pipeline()
            
            # Link elements
            if not self._link_elements():
                logger.error("Failed to link elements")
                return False
            
            # Set up pad probes for metadata extraction
            self._setup_pad_probes()
            
            logger.info("DeepStream pipeline created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating pipeline: {e}")
            return False
    
    def _create_elements(self, config: Dict[str, Any]):
        """Create GStreamer elements for the pipeline"""
        # Multi-URI source for multiple camera streams
        self.source = Gst.ElementFactory.make("nvmultiurisrcbin", "multi-source")
        if not self.source:
            logger.error("Failed to create nvmultiurisrcbin")
            raise Exception("Failed to create source element")
        
        # Stream multiplexer
        self.streammux = Gst.ElementFactory.make("nvstreammux", "stream-muxer")
        if not self.streammux:
            logger.error("Failed to create nvstreammux")
            raise Exception("Failed to create streammux element")
        
        # Primary inference engine (YOLO)
        self.pgie = Gst.ElementFactory.make("nvinfer", "primary-inference")
        if not self.pgie:
            logger.error("Failed to create nvinfer")
            raise Exception("Failed to create pgie element")
        
        # Tracker
        self.tracker = Gst.ElementFactory.make("nvtracker", "tracker")
        if not self.tracker:
            logger.error("Failed to create nvtracker")
            raise Exception("Failed to create tracker element")
        
        # Analytics plugin
        self.analytics = Gst.ElementFactory.make("nvdsanalytics", "analytics")
        if not self.analytics:
            logger.error("Failed to create nvdsanalytics")
            raise Exception("Failed to create analytics element")
        
        # TEE for splitting output
        self.tee = Gst.ElementFactory.make("tee", "output-tee")
        if not self.tee:
            logger.error("Failed to create tee")
            raise Exception("Failed to create tee element")
        
        # HLS sink branch
        self.hls_queue = Gst.ElementFactory.make("queue", "hls-queue")
        self.hls_tiler = Gst.ElementFactory.make("nvmultistreamtiler", "hls-tiler")
        self.hls_convert = Gst.ElementFactory.make("nvvideoconvert", "hls-convert")
        self.hls_encoder = Gst.ElementFactory.make("nvv4l2h264enc", "hls-encoder")
        self.hls_parser = Gst.ElementFactory.make("h264parse", "hls-parser")
        self.hls_mux = Gst.ElementFactory.make("mpegtsmux", "hls-mux")
        self.hls_sink = Gst.ElementFactory.make("hlssink3", "hls-sink")
        
        # Metadata sink branch
        self.meta_queue = Gst.ElementFactory.make("queue", "meta-queue")
        self.msg_converter = Gst.ElementFactory.make("nvmsgconv", "msg-converter")
        self.msg_broker = Gst.ElementFactory.make("nvmsgbroker", "msg-broker")
        
        # Configure elements
        self._configure_elements(config)
    
    def _configure_elements(self, config: Dict[str, Any]):
        """Configure GStreamer elements with parameters"""
        # Configure streammux
        self.streammux.set_property('width', 1920)
        self.streammux.set_property('height', 1080)
        self.streammux.set_property('batch-size', 1)
        self.streammux.set_property('batched-push-timeout', 4000000)
        
        # Configure primary inference
        self.pgie.set_property('config-file-path', '/opt/nvidia/deepstream/deepstream/configs/config_infer_primary.txt')
        
        # Configure tracker
        self.tracker.set_property('ll-lib-file', '/opt/nvidia/deepstream/deepstream/lib/libnvds_nvmultiobjecttracker.so')
        self.tracker.set_property('ll-config-file', '/opt/nvidia/deepstream/deepstream/configs/tracker_config.txt')
        
        # Configure analytics
        self.analytics.set_property('config-file', '/opt/nvidia/deepstream/deepstream/configs/analytics_config.txt')
        
        # Configure HLS sink
        self.hls_sink.set_property('location', '/opt/aries/streams/stream_%u/index.m3u8')
        self.hls_sink.set_property('playlist-length', 4)
        self.hls_sink.set_property('max-files', 10)
        self.hls_sink.set_property('target-duration', 2)
        
        # Configure message broker
        self.msg_broker.set_property('proto-lib', '/opt/nvidia/deepstream/deepstream/lib/libnvds_pulsar_proto.so')
        self.msg_broker.set_property('conn-str', os.getenv('PULSAR_URL', 'pulsar://localhost:6650'))
        self.msg_broker.set_property('topic', 'aries-metadata-raw')
        self.msg_broker.set_property('sync', False)
    
    def _add_elements_to_pipeline(self):
        """Add all elements to the pipeline"""
        elements = [
            self.source, self.streammux, self.pgie, self.tracker, self.analytics,
            self.tee, self.hls_queue, self.hls_tiler, self.hls_convert,
            self.hls_encoder, self.hls_parser, self.hls_mux, self.hls_sink,
            self.meta_queue, self.msg_converter, self.msg_broker
        ]
        
        for element in elements:
            if element:
                self.pipeline.add(element)
    
    def _link_elements(self) -> bool:
        """Link all elements in the pipeline"""
        try:
            # Link source to streammux (handled by nvmultiurisrcbin)
            # Link streammux to pgie
            if not self.streammux.link(self.pgie):
                logger.error("Failed to link streammux to pgie")
                return False
            
            # Link pgie to tracker
            if not self.pgie.link(self.tracker):
                logger.error("Failed to link pgie to tracker")
                return False
            
            # Link tracker to analytics
            if not self.tracker.link(self.analytics):
                logger.error("Failed to link tracker to analytics")
                return False
            
            # Link analytics to tee
            if not self.analytics.link(self.tee):
                logger.error("Failed to link analytics to tee")
                return False
            
            # Link HLS branch
            if not self.tee.link(self.hls_queue):
                logger.error("Failed to link tee to hls_queue")
                return False
            
            hls_elements = [self.hls_queue, self.hls_tiler, self.hls_convert, 
                          self.hls_encoder, self.hls_parser, self.hls_mux, self.hls_sink]
            
            for i in range(len(hls_elements) - 1):
                if not hls_elements[i].link(hls_elements[i + 1]):
                    logger.error(f"Failed to link {hls_elements[i].name} to {hls_elements[i + 1].name}")
                    return False
            
            # Link metadata branch
            if not self.tee.link(self.meta_queue):
                logger.error("Failed to link tee to meta_queue")
                return False
            
            if not self.meta_queue.link(self.msg_converter):
                logger.error("Failed to link meta_queue to msg_converter")
                return False
            
            if not self.msg_converter.link(self.msg_broker):
                logger.error("Failed to link msg_converter to msg_broker")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error linking elements: {e}")
            return False
    
    def _setup_pad_probes(self):
        """Set up pad probes for metadata extraction"""
        # Get sink pad of analytics element
        analytics_sink_pad = self.analytics.get_static_pad("sink")
        if not analytics_sink_pad:
            logger.error("Unable to get analytics sink pad")
            return
        
        # Add probe to extract metadata
        analytics_sink_pad.add_probe(Gst.PadProbeType.BUFFER, self.pad_buffer_probe, 0)
    
    def pad_buffer_probe(self, pad, info, u_data):
        """Pad probe to extract metadata from buffers"""
        try:
            gst_buffer = info.get_buffer()
            if not gst_buffer:
                return Gst.PadProbeReturn.OK
            
            # Get batch metadata
            batch_meta = pyds.gst_buffer_get_nvds_batch_meta(hash(gst_buffer))
            if not batch_meta:
                return Gst.PadProbeReturn.OK
            
            # Process each frame in the batch
            l_frame = batch_meta.frame_meta_list
            while l_frame is not None:
                try:
                    frame_meta = pyds.NvDsFrameMeta.cast(l_frame.data)
                    
                    # Process objects in this frame
                    self._process_frame_objects(frame_meta, batch_meta)
                    
                    # Get next frame
                    l_frame = l_frame.next
                    
                except StopIteration:
                    break
            
            return Gst.PadProbeReturn.OK
            
        except Exception as e:
            logger.error(f"Error in pad probe: {e}")
            return Gst.PadProbeReturn.OK
    
    def _process_frame_objects(self, frame_meta, batch_meta):
        """Process detected objects in a frame"""
        try:
            # Get object list
            l_obj = frame_meta.obj_meta_list
            
            while l_obj is not None:
                try:
                    obj_meta = pyds.NvDsObjectMeta.cast(l_obj.data)
                    
                    # Extract object information
                    object_info = {
                        'object_id': obj_meta.object_id,
                        'class_id': obj_meta.class_id,
                        'confidence': obj_meta.confidence,
                        'bbox': {
                            'left': obj_meta.rect_params.left,
                            'top': obj_meta.rect_params.top,
                            'width': obj_meta.rect_params.width,
                            'height': obj_meta.rect_params.height
                        }
                    }
                    
                    # Run analytics on this object
                    self._run_analytics(frame_meta, obj_meta, object_info)
                    
                    # Get next object
                    l_obj = l_obj.next
                    
                except StopIteration:
                    break
                    
        except Exception as e:
            logger.error(f"Error processing frame objects: {e}")
    
    def _run_analytics(self, frame_meta, obj_meta, object_info):
        """Run analytics on detected objects"""
        try:
            # Check if object is in defined ROI zones
            if self.config_service.is_point_in_roi(
                obj_meta.rect_params.left + obj_meta.rect_params.width / 2,
                obj_meta.rect_params.top + obj_meta.rect_params.height / 2
            ):
                # Create custom metadata for zone entry
                user_meta = pyds.nvds_acquire_user_meta_from_pool(frame_meta.batch_meta)
                if user_meta:
                    user_meta.base_meta.meta_type = pyds.NVDS_USER_FRAME_META_NVDSANALYTICS
                    
                    # Create alert payload
                    alert_payload = {
                        'event': 'zone_entry',
                        'object_id': obj_meta.object_id,
                        'timestamp': datetime.utcnow().isoformat(),
                        'camera_id': frame_meta.source_id,
                        'confidence': obj_meta.confidence,
                        'object_class': obj_meta.class_id
                    }
                    
                    # Attach payload to user meta (simplified - in production, use proper memory management)
                    user_meta.user_meta_data = json.dumps(alert_payload).encode('utf-8')
                    
                    # Add user meta to object
                    pyds.nvds_add_user_meta_to_obj(obj_meta, user_meta)
                    
                    logger.info(f"Zone entry detected: Object {obj_meta.object_id}")
            
        except Exception as e:
            logger.error(f"Error running analytics: {e}")
    
    def start_pipeline(self) -> bool:
        """Start the DeepStream pipeline"""
        try:
            if not self.pipeline:
                logger.error("Pipeline not created")
                return False
            
            # Set pipeline to playing state
            ret = self.pipeline.set_state(Gst.State.PLAYING)
            if ret == Gst.StateChangeReturn.FAILURE:
                logger.error("Failed to set pipeline to playing state")
                return False
            
            self.running = True
            logger.info("DeepStream pipeline started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error starting pipeline: {e}")
            return False
    
    def stop_pipeline(self) -> bool:
        """Stop the DeepStream pipeline"""
        try:
            if not self.pipeline:
                return True
            
            self.running = False
            
            # Send EOS event
            self.pipeline.send_event(Gst.Event.new_eos())
            
            # Wait for EOS
            bus = self.pipeline.get_bus()
            msg = bus.timed_pop_filtered(
                Gst.CLOCK_TIME_NONE,
                Gst.MessageType.EOS | Gst.MessageType.ERROR
            )
            
            # Set pipeline to NULL state
            self.pipeline.set_state(Gst.State.NULL)
            
            logger.info("DeepStream pipeline stopped successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping pipeline: {e}")
            return False
    
    def update_roi_config(self, new_config: Dict[str, Any]) -> bool:
        """Update ROI configuration dynamically"""
        try:
            if not self.analytics:
                logger.error("Analytics element not available")
                return False
            
            # Generate new config file
            config_content = self.config_service.generate_roi_config(new_config)
            config_path = "/tmp/analytics_dynamic.txt"
            
            # Write config file
            with open(config_path, 'w') as f:
                f.write(config_content)
            
            # Update analytics element property
            self.analytics.set_property('config-file', config_path)
            
            logger.info("ROI configuration updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error updating ROI config: {e}")
            return False

def main():
    """Main function to run the DeepStream pipeline"""
    try:
        # Create pipeline instance
        pipeline = DeepStreamPipeline()
        
        # Configuration
        config = {
            'camera_streams': [
                'rtsp://admin:password@192.168.1.100:554/stream1',
                'rtsp://admin:password@192.168.1.101:554/stream1'
            ],
            'roi_zones': [
                {
                    'name': 'entrance_zone',
                    'points': [(100, 100), (500, 100), (500, 400), (100, 400)]
                }
            ]
        }
        
        # Create pipeline
        if not pipeline.create_pipeline(config):
            logger.error("Failed to create pipeline")
            return 1
        
        # Start pipeline
        if not pipeline.start_pipeline():
            logger.error("Failed to start pipeline")
            return 1
        
        # Create main loop
        loop = GLib.MainLoop()
        
        # Set up signal handlers
        def signal_handler(sig, frame):
            logger.info("Received interrupt signal, stopping pipeline...")
            pipeline.stop_pipeline()
            loop.quit()
        
        import signal
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Run main loop
        logger.info("DeepStream pipeline running. Press Ctrl+C to stop.")
        loop.run()
        
        # Cleanup
        pipeline.stop_pipeline()
        
        return 0
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())