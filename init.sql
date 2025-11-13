-- Initialize Aries database with tables and sample data

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- Create cameras table
CREATE TABLE cameras (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    rtsp_uri TEXT NOT NULL,
    description TEXT,
    location VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    owner_id INTEGER REFERENCES users(id) ON DELETE CASCADE
);

-- Create models table
CREATE TABLE models (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    version VARCHAR(20) NOT NULL,
    model_type VARCHAR(50) DEFAULT 'yolov8',
    config_path TEXT NOT NULL,
    weights_path TEXT NOT NULL,
    labels_path TEXT NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    accuracy_metrics JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- Create analytics_jobs table
CREATE TABLE analytics_jobs (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    confidence_threshold FLOAT DEFAULT 0.5,
    nms_threshold FLOAT DEFAULT 0.4,
    max_detections INTEGER DEFAULT 100,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    camera_id INTEGER REFERENCES cameras(id) ON DELETE CASCADE,
    model_id INTEGER REFERENCES models(id) ON DELETE CASCADE,
    created_by_id INTEGER REFERENCES users(id) ON DELETE CASCADE
);

-- Create rois table
CREATE TABLE rois (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    polygon_points JSONB NOT NULL,
    roi_type VARCHAR(20) DEFAULT 'zone',
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    alert_on_entry BOOLEAN DEFAULT TRUE,
    alert_on_exit BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    analytics_job_id INTEGER REFERENCES analytics_jobs(id) ON DELETE CASCADE
);

-- Create alert_events table
CREATE TABLE alert_events (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    alert_type VARCHAR(50) NOT NULL,
    confidence FLOAT NOT NULL,
    object_class VARCHAR(50) NOT NULL,
    object_id VARCHAR(50),
    bbox_x FLOAT NOT NULL,
    bbox_y FLOAT NOT NULL,
    bbox_width FLOAT NOT NULL,
    bbox_height FLOAT NOT NULL,
    snapshot_path TEXT,
    metadata JSONB,
    processed BOOLEAN DEFAULT FALSE,
    camera_id INTEGER REFERENCES cameras(id) ON DELETE CASCADE,
    analytics_job_id INTEGER REFERENCES analytics_jobs(id) ON DELETE CASCADE
);

-- Create system_config table
CREATE TABLE system_config (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value JSONB NOT NULL,
    description TEXT,
    updated_at TIMESTAMP,
    updated_by VARCHAR(100)
);

-- Create indexes for better performance
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_cameras_owner_id ON cameras(owner_id);
CREATE INDEX idx_cameras_is_active ON cameras(is_active);
CREATE INDEX idx_analytics_jobs_camera_id ON analytics_jobs(camera_id);
CREATE INDEX idx_analytics_jobs_model_id ON analytics_jobs(model_id);
CREATE INDEX idx_analytics_jobs_created_by ON analytics_jobs(created_by_id);
CREATE INDEX idx_rois_analytics_job_id ON rois(analytics_job_id);
CREATE INDEX idx_alert_events_camera_id ON alert_events(camera_id);
CREATE INDEX idx_alert_events_analytics_job_id ON alert_events(analytics_job_id);
CREATE INDEX idx_alert_events_timestamp ON alert_events(timestamp);
CREATE INDEX idx_alert_events_alert_type ON alert_events(alert_type);
CREATE INDEX idx_alert_events_processed ON alert_events(processed);

-- Insert sample data
INSERT INTO users (username, email, hashed_password, full_name, is_superuser) VALUES 
('admin', 'admin@aries.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.PJ/..G', 'System Administrator', TRUE);

INSERT INTO models (name, version, model_type, config_path, weights_path, labels_path, description) VALUES 
('YOLOv8s', '8.0.0', 'yolov8', '/opt/nvidia/deepstream/deepstream/configs/config_infer_primary.txt', '/opt/nvidia/deepstream/deepstream/models/yolov8s.onnx', '/opt/nvidia/deepstream/deepstream/models/labels.txt', 'YOLOv8 Small model for object detection');

-- Grant permissions to application user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO aries;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO aries;