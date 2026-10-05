INSERT INTO locations (name, location_type, latitude, longitude, city, emirate) VALUES
('Burj Khalifa', 'landmark', 25.1972, 55.2744, 'Dubai', 'Dubai'),
('Dubai Mall', 'shopping', 25.1946, 55.2739, 'Dubai', 'Dubai'),
('Sheikh Zayed Mosque', 'mosque', 24.4137, 54.4671, 'Abu Dhabi', 'Abu Dhabi'),
('Marina Beach', 'beach', 25.0833, 55.1167, 'Dubai', 'Dubai'),
('Dune Camp', 'camp', 25.0630, 55.5390, 'Dubai', 'Dubai');

INSERT INTO routes (route_name, start_location_id, end_location_id, distance_km, estimated_duration_minutes) VALUES
(1, 1, 'Dubai City Tour', 25, 240),
(2, 4, 'Desert Safari Route', 45, 300),
(3, 5, 'Abu Dhabi Day Trip', 120, 480);

INSERT INTO poi (poi_name, poi_type, latitude, longitude, rating) VALUES
('Downtown Dubai', 'commercial', 25.1947, 55.2744, 4.8),
('Palm Jumeirah', 'landmark', 25.1409, 55.1469, 4.7),
('Corniche Abu Dhabi', 'waterfront', 24.4539, 54.3773, 4.6);

INSERT INTO geofences (geofence_name, center_latitude, center_longitude, radius_meters, geofence_type, alert_on_enter, alert_on_exit) VALUES
('Marina Dock Zone', 25.0833, 55.1167, 500, 'zone', TRUE, FALSE),
('Desert Camp Area', 25.0630, 55.5390, 2000, 'zone', TRUE, TRUE);
