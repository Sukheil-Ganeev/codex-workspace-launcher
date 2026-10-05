-- 01-CRM System Sample Data
-- Реалистичные данные для туристического бизнеса ОАЭ

-- Таблица companies
INSERT INTO companies (name, industry, website, country, city, phone, email, annual_revenue, employees_count) VALUES
('Al-Fardan Exchange', 'Finance', 'www.alfardan.ae', 'UAE', 'Dubai', '+971432345678', 'contact@alfardan.ae', 50000000, 250),
('Emirates NBD', 'Banking', 'www.emiratesnbd.com', 'UAE', 'Dubai', '+971431234567', 'info@emiratesnbd.com', 150000000, 8000),
('Emaar Properties', 'Real Estate', 'www.emaar.com', 'UAE', 'Dubai', '+971432123456', 'investors@emaar.com', 300000000, 5000),
('DP World', 'Logistics', 'www.dpworld.com', 'UAE', 'Dubai', '+971432456789', 'contact@dpworld.com', 200000000, 3500),
('ADIB', 'Banking', 'www.adib.ae', 'UAE', 'Abu Dhabi', '+971234567890', 'info@adib.ae', 120000000, 4000),
('Rotana Hotels', 'Hospitality', 'www.rotana.com', 'UAE', 'Dubai', '+971432987654', 'reservations@rotana.com', 80000000, 2000),
('Spinneys', 'Retail', 'www.spinneys.ae', 'UAE', 'Dubai', '+971432111111', 'customer@spinneys.ae', 45000000, 3000),
('Landmark Group', 'Retail', 'www.landmarkgroup.com', 'UAE', 'Dubai', '+971432222222', 'info@landmarkgroup.com', 100000000, 5000),
('RAK Petroleum', 'Energy', 'www.rakpetroleum.ae', 'UAE', 'Ras Al Khaimah', '+971723456789', 'info@rakpetroleum.ae', 250000000, 1500),
('Damas Jewellery', 'Luxury', 'www.damasjewellery.com', 'UAE', 'Dubai', '+971432345670', 'corporate@damas.ae', 35000000, 800);

-- Таблица contact_sources
INSERT INTO contact_sources (name, description, category) VALUES
('Website', 'Contact acquired from company website', 'website'),
('LinkedIn', 'Professional network referral', 'social'),
('Referral', 'Referred by existing customer', 'referral'),
('Trade Show', 'Met at Dubai Business Forum', 'event'),
('Cold Call', 'Outbound sales call', 'cold-call'),
('Email Campaign', 'From marketing email campaign', 'advertising'),
('WhatsApp', 'WhatsApp business message', 'messaging'),
('Google Ads', 'From Google Ads campaign', 'advertising'),
('Instagram', 'Referred from Instagram post', 'social'),
('Event', 'Dubai Travel Expo 2025', 'event');

-- Таблица contacts
INSERT INTO contacts (company_id, first_name, last_name, email, phone, mobile, position, department, country, city, language) VALUES
(1, 'Ahmed', 'Al-Mansouri', 'ahmed.almansouri@alfardan.ae', '+971432345678', '+971501234567', 'General Manager', 'Operations', 'UAE', 'Dubai', 'Arabic'),
(1, 'Fatima', 'Al-Mazrouei', 'fatima.mazrouei@alfardan.ae', '+971432345679', '+971501234568', 'HR Director', 'Human Resources', 'UAE', 'Dubai', 'Arabic'),
(2, 'Mohammed', 'Al-Suwaidi', 'm.alsuwaidi@emiratesnbd.com', '+971431234567', '+971505678901', 'VP Operations', 'Operations', 'UAE', 'Dubai', 'Arabic'),
(2, 'Elena', 'Petrova', 'e.petrova@emiratesnbd.com', '+971431234568', '+971509876543', 'Marketing Manager', 'Marketing', 'Russia', 'Dubai', 'Russian'),
(3, 'Sergei', 'Volkov', 's.volkov@emaar.com', '+971432123456', '+971502468135', 'Sales Director', 'Sales', 'Russia', 'Dubai', 'Russian'),
(3, 'Amira', 'Khan', 'a.khan@emaar.com', '+971432123457', '+971503691357', 'Project Manager', 'Projects', 'UAE', 'Dubai', 'English'),
(4, 'Viktor', 'Smirnov', 'v.smirnov@dpworld.com', '+971432456789', '+971504135792', 'Operations Manager', 'Operations', 'Russia', 'Dubai', 'Russian'),
(4, 'Noor', 'Al-Kaabi', 'n.alkaabi@dpworld.com', '+971432456790', '+971505792468', 'Business Analyst', 'Analysis', 'UAE', 'Dubai', 'Arabic'),
(5, 'Yuri', 'Petrov', 'y.petrov@adib.ae', '+971234567890', '+971506543210', 'Finance Manager', 'Finance', 'Russia', 'Abu Dhabi', 'Russian'),
(5, 'Layla', 'Hassan', 'l.hassan@adib.ae', '+971234567891', '+971506543211', 'Compliance Officer', 'Compliance', 'UAE', 'Abu Dhabi', 'English'),
(6, 'Dmitri', 'Kuznetsov', 'd.kuznetsov@rotana.com', '+971432987654', '+971507654321', 'Hotel Manager', 'Operations', 'Russia', 'Dubai', 'Russian'),
(6, 'Zara', 'Al-Marri', 'z.almarri@rotana.com', '+971432987655', '+971507654322', 'Events Coordinator', 'Events', 'UAE', 'Dubai', 'Arabic'),
(7, 'Andrey', 'Sokolov', 'a.sokolov@spinneys.ae', '+971432111111', '+971508765432', 'Supply Chain Director', 'Logistics', 'Russia', 'Dubai', 'Russian'),
(7, 'Hana', 'Al-Otaiba', 'h.alotaiba@spinneys.ae', '+971432111112', '+971508765433', 'Store Manager', 'Retail', 'UAE', 'Dubai', 'English'),
(8, 'Alexei', 'Kozlov', 'a.kozlov@landmarkgroup.com', '+971432222222', '+971509876544', 'Regional Director', 'Management', 'Russia', 'Dubai', 'Russian'),
(8, 'Salma', 'Al-Neyadi', 's.alneyadi@landmarkgroup.com', '+971432222223', '+971509876545', 'Marketing Specialist', 'Marketing', 'UAE', 'Dubai', 'Arabic'),
(9, 'Pavel', 'Orlov', 'p.orlov@rakpetroleum.ae', '+971723456789', '+971701234567', 'CEO', 'Executive', 'Russia', 'Ras Al Khaimah', 'Russian'),
(9, 'Nadia', 'Al-Khayat', 'n.alkhayat@rakpetroleum.ae', '+971723456790', '+971701234568', 'CFO', 'Finance', 'UAE', 'Ras Al Khaimah', 'English'),
(10, 'Vladimir', 'Lebedev', 'v.lebedev@damas.ae', '+971432345670', '+971501111111', 'Business Development', 'Sales', 'Russia', 'Dubai', 'Russian'),
(10, 'Lina', 'Al-Rashid', 'l.alrashid@damas.ae', '+971432345671', '+971501111112', 'Customer Relations', 'Sales', 'UAE', 'Dubai', 'Arabic');

-- Таблица customer_segments
INSERT INTO customer_segments (name, description) VALUES
('Enterprise', 'Large corporations with high budget'),
('Mid-Market', 'Medium-sized companies'),
('SMB', 'Small and medium businesses'),
('Startup', 'New emerging businesses'),
('Government', 'Government and public sector'),
('VIP', 'High-value premium clients'),
('Educational', 'Universities and schools'),
('Corporate Groups', 'Companies organizing group tours');

-- Таблица contact_tags
INSERT INTO contact_tags (name, color, description) VALUES
('VIP', '#FF0000', 'Very Important Person - Priority contact'),
('Recurring', '#00FF00', 'Repeating customer'),
('New', '#0000FF', 'New contact within 3 months'),
('Decision Maker', '#FFD700', 'Person with decision authority'),
('Budget Holder', '#FFA500', 'Controls budget allocation'),
('Technical', '#9370DB', 'Technical specialist'),
('Stakeholder', '#20B2AA', 'Key project stakeholder'),
('Inactive', '#808080', 'No recent activity in 6+ months');

-- Таблица customer_classifications
INSERT INTO customer_classifications (contact_id, segment_id, priority, lifetime_value) VALUES
(1, 1, 'hot', 250000.00),
(2, 1, 'warm', 180000.00),
(3, 1, 'hot', 320000.00),
(4, 2, 'warm', 95000.00),
(5, 1, 'vip', 500000.00),
(6, 2, 'warm', 120000.00),
(7, 1, 'hot', 280000.00),
(8, 2, 'warm', 85000.00),
(9, 1, 'vip', 450000.00),
(10, 2, 'cold', 45000.00),
(11, 3, 'hot', 150000.00),
(12, 2, 'warm', 100000.00),
(13, 1, 'hot', 275000.00),
(14, 2, 'warm', 90000.00),
(15, 1, 'vip', 480000.00),
(16, 2, 'warm', 110000.00),
(17, 1, 'hot', 350000.00),
(18, 1, 'warm', 200000.00),
(19, 2, 'warm', 125000.00),
(20, 2, 'warm', 95000.00);

-- Таблица communication_preferences
INSERT INTO communication_preferences (contact_id, prefers_email, prefers_phone, prefers_sms, prefers_whatsapp, language_preference) VALUES
(1, TRUE, TRUE, FALSE, TRUE, 'Arabic'),
(2, TRUE, TRUE, TRUE, TRUE, 'Arabic'),
(3, TRUE, TRUE, FALSE, FALSE, 'Arabic'),
(4, TRUE, TRUE, TRUE, TRUE, 'Russian'),
(5, TRUE, FALSE, FALSE, TRUE, 'Russian'),
(6, TRUE, TRUE, TRUE, FALSE, 'English'),
(7, TRUE, TRUE, FALSE, TRUE, 'Russian'),
(8, TRUE, TRUE, TRUE, FALSE, 'English'),
(9, TRUE, TRUE, FALSE, TRUE, 'Russian'),
(10, FALSE, TRUE, FALSE, FALSE, 'Arabic'),
(11, TRUE, TRUE, FALSE, TRUE, 'Russian'),
(12, TRUE, TRUE, TRUE, FALSE, 'English'),
(13, TRUE, FALSE, FALSE, TRUE, 'Russian'),
(14, TRUE, TRUE, TRUE, FALSE, 'English'),
(15, TRUE, TRUE, FALSE, TRUE, 'Russian'),
(16, TRUE, TRUE, TRUE, FALSE, 'Arabic'),
(17, TRUE, TRUE, FALSE, TRUE, 'Russian'),
(18, TRUE, TRUE, TRUE, TRUE, 'Russian'),
(19, TRUE, FALSE, FALSE, FALSE, 'English'),
(20, TRUE, TRUE, TRUE, FALSE, 'Arabic');

-- Таблица mailing_lists
INSERT INTO mailing_lists (name, description, purpose) VALUES
('Tour Promotions', 'New tour packages and special offers', 'marketing'),
('Newsletter', 'Monthly business newsletter', 'newsletter'),
('Event Announcements', 'Upcoming events and exhibitions', 'announcements'),
('Product Updates', 'New features and services', 'marketing'),
('Exclusive Deals', 'VIP exclusive offers', 'marketing'),
('Corporate News', 'Company updates and news', 'announcements');

-- Таблица mailing_list_subscriptions
INSERT INTO mailing_list_subscriptions (mailing_list_id, contact_id, is_active) VALUES
(1, 1, TRUE), (1, 3, TRUE), (1, 5, TRUE), (1, 7, TRUE), (1, 9, TRUE),
(2, 2, TRUE), (2, 4, TRUE), (2, 6, TRUE), (2, 8, TRUE), (2, 10, TRUE),
(3, 11, TRUE), (3, 12, TRUE), (3, 13, TRUE), (3, 14, TRUE), (3, 15, TRUE),
(4, 16, TRUE), (4, 17, TRUE), (4, 18, TRUE), (4, 19, TRUE), (4, 20, TRUE),
(5, 1, TRUE), (5, 3, TRUE), (5, 5, TRUE), (5, 7, TRUE), (5, 9, TRUE),
(6, 2, TRUE), (6, 4, TRUE), (6, 6, TRUE), (6, 8, TRUE), (6, 10, TRUE);

-- Таблица tasks
INSERT INTO tasks (contact_id, title, description, priority, status, due_date, assigned_to) VALUES
(1, 'Follow up on Dubai tour proposal', 'Confirm participation in group tour for 50 people', 'high', 'open', CURRENT_DATE + INTERVAL '5 days', 'Suhail'),
(3, 'Discuss yacht charter options', 'Company team building event planning', 'hot', 'in-progress', CURRENT_DATE + INTERVAL '3 days', 'Suhail'),
(5, 'Review contract terms', 'Annual tour package agreement', 'critical', 'open', CURRENT_DATE + INTERVAL '1 day', 'Marcel'),
(7, 'Arrange car rental quotes', 'Fleet transportation for corporate event', 'high', 'open', CURRENT_DATE + INTERVAL '4 days', 'Suhail'),
(9, 'Schedule meeting for partnership', 'Potential collaboration on travel packages', 'warm', 'pending', CURRENT_DATE + INTERVAL '7 days', 'Suhail'),
(11, 'Send hotel recommendations', 'List of 4-5 star hotels in Dubai area', 'medium', 'completed', CURRENT_DATE - INTERVAL '2 days', 'Assistant'),
(13, 'Confirm booking details', 'Desert safari tour for 30 participants', 'high', 'open', CURRENT_DATE + INTERVAL '2 days', 'Suhail'),
(15, 'VIP client appreciation', 'Plan exclusive yacht experience', 'critical', 'in-progress', CURRENT_DATE + INTERVAL '6 days', 'Suhail'),
(17, 'Transport service inquiry', 'Airport transfers and daily tours', 'medium', 'open', CURRENT_DATE + INTERVAL '5 days', 'Marcel'),
(19, 'Negotiate volume discount', 'Multiple tours for company retreat', 'high', 'open', CURRENT_DATE + INTERVAL '3 days', 'Suhail');

-- Таблица contact_history
INSERT INTO contact_history (contact_id, source_id, interaction_type, notes, duration_minutes, next_follow_up, status, created_by) VALUES
(1, 1, 'call', 'Discussed group tour for 40 employees', 35, CURRENT_DATE + INTERVAL '7 days', 'completed', 'Suhail'),
(3, 3, 'meeting', 'Face-to-face meeting at office about desert safari', 60, CURRENT_DATE + INTERVAL '5 days', 'completed', 'Suhail'),
(5, 2, 'email', 'Sent detailed tour packages and pricing', 0, CURRENT_DATE + INTERVAL '3 days', 'completed', 'Suhail'),
(7, 10, 'call', 'Inquiry about yacht charter for team building', 25, CURRENT_DATE + INTERVAL '4 days', 'completed', 'Suhail'),
(9, 5, 'meeting', 'Partnership discussion at Dubai Business Forum', 90, CURRENT_DATE + INTERVAL '10 days', 'completed', 'Suhail'),
(11, 4, 'email', 'Sent confirmation for desert safari booking', 0, CURRENT_DATE + INTERVAL '2 days', 'completed', 'Assistant'),
(13, 1, 'call', 'Confirmed dates and number of participants', 20, CURRENT_DATE + INTERVAL '6 days', 'completed', 'Suhail'),
(15, 2, 'message', 'WhatsApp discussion about exclusive yacht experience', 15, CURRENT_DATE + INTERVAL '8 days', 'completed', 'Suhail'),
(17, 9, 'email', 'Sent car rental options and rates', 0, CURRENT_DATE + INTERVAL '4 days', 'pending', 'Marcel'),
(19, 6, 'call', 'Negotiating volume discount for 5-day tours', 40, CURRENT_DATE + INTERVAL '3 days', 'completed', 'Suhail'),
(2, 1, 'email', 'Sent HR team building package', 0, CURRENT_DATE + INTERVAL '5 days', 'completed', 'Assistant'),
(4, 2, 'meeting', 'Discussed marketing tour sponsorship', 45, CURRENT_DATE + INTERVAL '7 days', 'completed', 'Suhail'),
(6, 3, 'call', 'Project team outing planning', 30, CURRENT_DATE + INTERVAL '4 days', 'completed', 'Suhail'),
(8, 1, 'email', 'Inquiry about logistics tour and training', 0, CURRENT_DATE + INTERVAL '6 days', 'pending', 'Assistant'),
(10, 4, 'call', 'Checked if interested in future tours', 20, NULL, 'completed', 'Suhail'),
(12, 2, 'message', 'WhatsApp: Confirmed hotel room availability', 10, CURRENT_DATE + INTERVAL '2 days', 'completed', 'Assistant'),
(14, 1, 'email', 'Sent retail team tour package', 0, CURRENT_DATE + INTERVAL '5 days', 'completed', 'Assistant'),
(16, 6, 'call', 'Sales follow-up on group tour interest', 25, CURRENT_DATE + INTERVAL '4 days', 'completed', 'Suhail'),
(18, 2, 'meeting', 'Discussed annual company trip planning', 75, CURRENT_DATE + INTERVAL '9 days', 'completed', 'Suhail'),
(20, 3, 'email', 'Sent jewelry store team tour proposal', 0, CURRENT_DATE + INTERVAL '5 days', 'pending', 'Assistant');
