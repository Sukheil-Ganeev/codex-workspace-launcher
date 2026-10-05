-- 05-Finance System Schema
CREATE TABLE currency_rates (id SERIAL PRIMARY KEY, from_currency VARCHAR(3), to_currency VARCHAR(3), rate NUMERIC(10,6), updated_at TIMESTAMPTZ);
CREATE TABLE invoices (id SERIAL PRIMARY KEY, invoice_number VARCHAR(50) UNIQUE NOT NULL, booking_id INTEGER, company_id INTEGER, amount NUMERIC(12,2), currency VARCHAR(3), invoice_date DATE, due_date DATE, status VARCHAR(50), created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE invoice_items (id SERIAL PRIMARY KEY, invoice_id INTEGER REFERENCES invoices(id), description VARCHAR(255), quantity INTEGER, unit_price NUMERIC(10,2), total_price NUMERIC(12,2));
CREATE TABLE expenses (id SERIAL PRIMARY KEY, expense_type VARCHAR(100), amount NUMERIC(12,2), currency VARCHAR(3), expense_date DATE, description TEXT, category VARCHAR(100), status VARCHAR(50), created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE revenue_streams (id SERIAL PRIMARY KEY, stream_name VARCHAR(255), revenue_type VARCHAR(50), monthly_target NUMERIC(15,2), currency VARCHAR(3), ytd_revenue NUMERIC(15,2));
CREATE TABLE financial_reports (id SERIAL PRIMARY KEY, report_type VARCHAR(100), report_date DATE, total_revenue NUMERIC(15,2), total_expenses NUMERIC(15,2), net_profit NUMERIC(15,2), generated_at TIMESTAMPTZ);
CREATE TABLE tax_records (id SERIAL PRIMARY KEY, tax_period VARCHAR(50), tax_type VARCHAR(100), amount NUMERIC(12,2), due_date DATE, status VARCHAR(50));
