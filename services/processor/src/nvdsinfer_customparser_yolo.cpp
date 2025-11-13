/***********************************************************************************************
 * Copyright (c) 2021, Aries-Edge Platform
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *     * Redistributions of source code must retain the above copyright
 *       notice, this list of conditions and the following disclaimer.
 *     * Redistributions in binary form must reproduce the above copyright
 *       notice, this list of conditions and the following disclaimer in the
 *       documentation and/or other materials provided with the distribution.
 *     * Neither the name of the Aries-Edge Platform nor the
 *       names of its contributors may be used to endorse or promote products
 *       derived from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 * WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY
 * DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 * ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 ***********************************************************************************************/

#include "nvdsinfer_custom_impl.h"
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstring>
#include <cuda_runtime_api.h>
#include <iostream>
#include <vector>

#define MIN(a,b) ((a) < (b) ? (a) : (b))
#define MAX(a,b) ((a) > (b) ? (a) : (b))
#define CLIP(a,min,max) (MAX(MIN(a, max), min))

static constexpr int LOCATIONS = 4;
struct alignas(float) Detection {
    float bbox[LOCATIONS];  // x1, y1, x2, y2
    float conf;            // confidence
    float class_id;        // class id
};

extern "C" bool NvDsInferParseYolo (
    std::vector<NvDsInferLayerInfo> const &outputLayersInfo,
    NvDsInferNetworkInfo const &networkInfo,
    NvDsInferParseDetectionParams const &detectionParams,
    std::vector<NvDsInferParseObjectInfo> &objectList);

extern "C" bool NvDsInferParseYoloV8 (
    std::vector<NvDsInferLayerInfo> const &outputLayersInfo,
    NvDsInferNetworkInfo const &networkInfo,
    NvDsInferParseDetectionParams const &detectionParams,
    std::vector<NvDsInferParseObjectInfo> &objectList);

static std::vector<Detection> decodeYoloV8Tensor(
    const float* output,
    const uint outputSize,
    const uint numClasses,
    const float confThresh) {
    
    std::vector<Detection> detections;
    const uint detSize = numClasses + LOCATIONS; // 80 classes + 4 bbox coords
    
    for (uint i = 0; i < outputSize; i += detSize) {
        const float* ptr = output + i;
        float maxScore = 0.0f;
        int maxIdx = 0;
        
        // Find max class score
        for (uint j = LOCATIONS; j < detSize; j++) {
            if (ptr[j] > maxScore) {
                maxScore = ptr[j];
                maxIdx = j - LOCATIONS;
            }
        }
        
        if (maxScore >= confThresh) {
            Detection det;
            det.bbox[0] = ptr[0]; // x1
            det.bbox[1] = ptr[1]; // y1  
            det.bbox[2] = ptr[2]; // x2
            det.bbox[3] = ptr[3]; // y2
            det.conf = maxScore;
            det.class_id = maxIdx;
            detections.push_back(det);
        }
    }
    
    return detections;
}

static std::vector<Detection> decodeYoloV5Tensor(
    const float* output,
    const uint outputSize,
    const uint numClasses,
    const float confThresh) {
    
    std::vector<Detection> detections;
    const uint detSize = numClasses + LOCATIONS + 1; // 80 classes + 4 bbox + 1 conf
    
    for (uint i = 0; i < outputSize; i += detSize) {
        const float* ptr = output + i;
        float conf = ptr[4];
        
        if (conf >= confThresh) {
            float maxScore = 0.0f;
            int maxIdx = 0;
            
            // Find max class score
            for (uint j = LOCATIONS + 1; j < detSize; j++) {
                float score = conf * ptr[j];
                if (score > maxScore) {
                    maxScore = score;
                    maxIdx = j - (LOCATIONS + 1);
                }
            }
            
            if (maxScore >= confThresh) {
                Detection det;
                det.bbox[0] = ptr[0] - ptr[2] / 2; // center_x - width/2
                det.bbox[1] = ptr[1] - ptr[3] / 2; // center_y - height/2
                det.bbox[2] = ptr[0] + ptr[2] / 2; // center_x + width/2
                det.bbox[3] = ptr[1] + ptr[3] / 2; // center_y + height/2
                det.conf = maxScore;
                det.class_id = maxIdx;
                detections.push_back(det);
            }
        }
    }
    
    return detections;
}

static float iou(const Detection& a, const Detection& b) {
    float x1 = MAX(a.bbox[0], b.bbox[0]);
    float y1 = MAX(a.bbox[1], b.bbox[1]);
    float x2 = MIN(a.bbox[2], b.bbox[2]);
    float y2 = MIN(a.bbox[3], b.bbox[3]);
    
    float intersection = MAX(0, x2 - x1) * MAX(0, y2 - y1);
    float areaA = (a.bbox[2] - a.bbox[0]) * (a.bbox[3] - a.bbox[1]);
    float areaB = (b.bbox[2] - b.bbox[0]) * (b.bbox[3] - b.bbox[1]);
    float unionArea = areaA + areaB - intersection;
    
    return intersection / unionArea;
}

static std::vector<Detection> nms(std::vector<Detection>& detections, float nmsThresh) {
    std::sort(detections.begin(), detections.end(), 
        [](const Detection& a, const Detection& b) {
            return a.conf > b.conf;
        });
    
    std::vector<Detection> result;
    std::vector<bool> suppressed(detections.size(), false);
    
    for (size_t i = 0; i < detections.size(); i++) {
        if (suppressed[i]) continue;
        
        result.push_back(detections[i]);
        
        for (size_t j = i + 1; j < detections.size(); j++) {
            if (suppressed[j]) continue;
            
            if (iou(detections[i], detections[j]) > nmsThresh) {
                suppressed[j] = true;
            }
        }
    }
    
    return result;
}

extern "C" bool NvDsInferParseYoloV8(
    std::vector<NvDsInferLayerInfo> const &outputLayersInfo,
    NvDsInferNetworkInfo const &networkInfo,
    NvDsInferParseDetectionParams const &detectionParams,
    std::vector<NvDsInferParseObjectInfo> &objectList) {
    
    if (outputLayersInfo.empty()) {
        std::cerr << "ERROR: No output layer info provided" << std::endl;
        return false;
    }
    
    const NvDsInferLayerInfo &layer = outputLayersInfo[0];
    const float* output = (const float*)layer.buffer;
    const uint outputSize = layer.inferDims.numElements;
    
    const float confThresh = detectionParams.perClassPreclusterThreshold[0];
    const float nmsThresh = 0.45f;
    const uint numClasses = 80; // COCO dataset classes
    
    // Decode YOLOv8 tensor
    std::vector<Detection> detections = decodeYoloV8Tensor(output, outputSize, numClasses, confThresh);
    
    // Apply NMS
    detections = nms(detections, nmsThresh);
    
    // Convert to NvDsInferParseObjectInfo
    for (const auto& det : detections) {
        NvDsInferParseObjectInfo obj;
        
        // Convert from normalized coordinates to pixel coordinates
        obj.classId = (uint)det.class_id;
        obj.detectionConfidence = det.conf;
        
        obj.left = CLIP(det.bbox[0] * networkInfo.width, 0, networkInfo.width - 1);
        obj.top = CLIP(det.bbox[1] * networkInfo.height, 0, networkInfo.height - 1);
        obj.width = CLIP((det.bbox[2] - det.bbox[0]) * networkInfo.width, 0, networkInfo.width - obj.left);
        obj.height = CLIP((det.bbox[3] - det.bbox[1]) * networkInfo.height, 0, networkInfo.height - obj.top);
        
        objectList.push_back(obj);
    }
    
    return true;
}

extern "C" bool NvDsInferParseYolo(
    std::vector<NvDsInferLayerInfo> const &outputLayersInfo,
    NvDsInferNetworkInfo const &networkInfo,
    NvDsInferParseDetectionParams const &detectionParams,
    std::vector<NvDsInferParseObjectInfo> &objectList) {
    
    return NvDsInferParseYoloV8(outputLayersInfo, networkInfo, detectionParams, objectList);
}

CHECK_CUSTOM_PARSE_FUNC_PROTOTYPE(NvDsInferParseYoloV8);
CHECK_CUSTOM_PARSE_FUNC_PROTOTYPE(NvDsInferParseYolo);