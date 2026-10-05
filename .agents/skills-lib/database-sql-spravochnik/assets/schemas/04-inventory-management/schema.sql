-- 04-Inventory Management Schema
-- Управление инвентарем, оборудованием, яхтами и техническим обслуживанием

CREATE TABLE inventory_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE inventory_items (
    id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES inventory_categories(id) ON DELETE SET NULL ON UPDATE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    sku VARCHAR(100) UNIQUE,
    quantity_on_hand INTEGER DEFAULT 0 CHECK (quantity_on_hand >= 0),
    reorder_level INTEGER,
    unit_cost NUMERIC(10,2) CHECK (unit_cost >= 0),
    unit_price NUMERIC(10,2) CHECK (unit_price >= 0),
    last_stock_check DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE stock_movements (
    id SERIAL PRIMARY KEY,
    item_id INTEGER NOT NULL REFERENCES inventory_items(id) ON DELETE CASCADE ON UPDATE CASCADE,
    movement_type VARCHAR(50), -- in, out, adjustment, transfer
    quantity INTEGER NOT NULL,
    reference_id INTEGER, -- booking_id, maintenance_id
    notes TEXT,
    created_by VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE yacht_maintenance (
    id SERIAL PRIMARY KEY,
    vehicle_id INTEGER NOT NULL,
    maintenance_type VARCHAR(100), -- engine, hull, electrical, interior
    maintenance_date DATE NOT NULL,
    next_due_date DATE,
    cost NUMERIC(12,2) CHECK (cost >= 0),
    contractor VARCHAR(255),
    description TEXT,
    status VARCHAR(50), -- scheduled, completed, pending
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE vehicle_maintenance (
    id SERIAL PRIMARY KEY,
    vehicle_id INTEGER NOT NULL,
    maintenance_type VARCHAR(100), -- oil, tires, brakes, inspection
    maintenance_date DATE NOT NULL,
    next_due_date DATE,
    mileage_km INTEGER,
    cost NUMERIC(12,2) CHECK (cost >= 0),
    contractor VARCHAR(255),
    description TEXT,
    status VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE equipment_maintenance (
    id SERIAL PRIMARY KEY,
    equipment_id INTEGER NOT NULL,
    equipment_type VARCHAR(100), -- yacht, vehicle, diving_equipment, camera
    maintenance_date DATE NOT NULL,
    next_due_date DATE,
    cost NUMERIC(12,2) CHECK (cost >= 0),
    description TEXT,
    status VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE insurance_policies (
    id SERIAL PRIMARY KEY,
    asset_type VARCHAR(100) NOT NULL, -- yacht, vehicle, general_liability
    asset_id INTEGER,
    asset_name VARCHAR(255),
    policy_number VARCHAR(100) UNIQUE,
    provider VARCHAR(255) NOT NULL,
    coverage_amount NUMERIC(15,2),
    premium NUMERIC(12,2) CHECK (premium >= 0),
    policy_start_date DATE NOT NULL,
    policy_expiry_date DATE NOT NULL,
    claim_history TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE licenses_and_certifications (
    id SERIAL PRIMARY KEY,
    person_id INTEGER,
    person_name VARCHAR(255),
    license_type VARCHAR(100), -- pilot, maritime, diving, driver
    license_number VARCHAR(100) UNIQUE,
    issued_by VARCHAR(255),
    issued_date DATE,
    expiry_date DATE NOT NULL,
    renewal_date DATE,
    status VARCHAR(50), -- active, expired, pending_renewal
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE asset_depreciation (
    id SERIAL PRIMARY KEY,
    asset_type VARCHAR(100),
    asset_id INTEGER,
    asset_name VARCHAR(255),
    purchase_date DATE,
    purchase_price NUMERIC(15,2),
    depreciation_method VARCHAR(50), -- straight_line, accelerated
    useful_life_years INTEGER,
    salvage_value NUMERIC(15,2),
    current_book_value NUMERIC(15,2),
    annual_depreciation NUMERIC(15,2),
    last_calculated_at TIMESTAMPTZ
);

CREATE TABLE storage_locations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    location_type VARCHAR(50), -- warehouse, dock, garage, office
    address VARCHAR(255),
    capacity_units VARCHAR(100),
    current_occupancy VARCHAR(100),
    is_climate_controlled BOOLEAN,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE inventory_allocation (
    id SERIAL PRIMARY KEY,
    item_id INTEGER NOT NULL REFERENCES inventory_items(id),
    storage_location_id INTEGER REFERENCES storage_locations(id),
    allocated_quantity INTEGER NOT NULL CHECK (allocated_quantity > 0),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
