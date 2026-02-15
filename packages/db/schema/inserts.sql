-- Sample data inserts for From Field to You agricultural supply chain system
-- This file contains mock data for testing and development purposes

--------------------------------------------------
-- CATEGORIES
--------------------------------------------------
INSERT INTO category (name, description) VALUES
('Vegetables', 'Fresh vegetables and leafy greens'),
('Fruits', 'Fresh seasonal fruits and berries'),
('Herbs', 'Fresh culinary herbs and aromatics');

--------------------------------------------------
-- UNIT LABELS
--------------------------------------------------
INSERT INTO unit_label (name, abbreviation, description) VALUES
('lb', 'lb', 'Pound'),
('ear', 'ea', 'Per ear (corn)'),
('head', 'head', 'Per head (lettuce)'),
('bag', 'bag', 'Per bag'),
('bunch', 'bunch', 'Per bunch'),
('pint', 'pt', 'Pint container'),
('pack', 'pack', 'Per pack');

--------------------------------------------------
-- FARMERS
--------------------------------------------------
-- Note: Only one farmer (admin) for single farmer system
-- Password: 'admin123' hashed with bcrypt
INSERT INTO farmer (name, farm_name, email, password_hash, phone, address_line1, city, postal_code, country, is_active, description, farm_type, farm_size_acres, established_year, certifications, website, business_hours) VALUES
('John Green', 'Green Valley Farm', 'john@greenvalley.com', '$2b$12$2Qz1dL1ey8g4wEKory9Mx.uYjDXqYL2AqrHWjj3doT61rbagWhRIi', '(555) 123-4567', '123 Farm Road', 'Springfield', '62701', 'Israel', true, 'Green Valley Farm has been growing fresh, sustainable produce for over 15 years. We specialize in organic vegetables, herbs, and fruits using traditional farming methods. Our single-farmer system ensures quality control and direct customer relationships.', 'Mixed Organic', 40.0, 2009, '["USDA Organic", "Certified Naturally Grown"]', 'https://greenvalleyfarm.com', 'Mon-Sat 8:00-18:00');

--------------------------------------------------
-- CUSTOMERS
--------------------------------------------------
-- Password: 'password123' hashed with bcrypt for all sample customers
INSERT INTO customer (first_name, last_name, email, password_hash, phone, address_line1, city, postal_code, country, marketing_opt_in) VALUES
('Alice', 'Johnson', 'alice@example.com', '$2b$12$RCD0wQVhsRQkfiUWa5aFH.J7Jn.lWGLr2dEP2dLZxduFHqKgeYAoK', '(555) 111-2222', '789 Main Street', 'Springfield', '62701', 'Israel', true),
('Bob', 'Smith', 'bob@example.com', '$2b$12$RCD0wQVhsRQkfiUWa5aFH.J7Jn.lWGLr2dEP2dLZxduFHqKgeYAoK', '(555) 333-4444', '321 Oak Avenue', 'Springfield', '62703', 'Israel', false),
('Carol', 'Davis', 'carol@example.com', '$2b$12$RCD0wQVhsRQkfiUWa5aFH.J7Jn.lWGLr2dEP2dLZxduFHqKgeYAoK', '(555) 555-6666', '456 Pine Street', 'Bloomington', '61701', 'Israel', true),
('David', 'Wilson', 'david@example.com', '$2b$12$RCD0wQVhsRQkfiUWa5aFH.J7Jn.lWGLr2dEP2dLZxduFHqKgeYAoK', '(555) 777-8888', '654 Elm Road', 'Champaign', '61820', 'Israel', true),
('Emma', 'Taylor', 'emma@example.com', '$2b$12$RCD0wQVhsRQkfiUWa5aFH.J7Jn.lWGLr2dEP2dLZxduFHqKgeYAoK', '(555) 999-0000', '987 Maple Lane', 'Springfield', '62704', 'Israel', false);

--------------------------------------------------
-- PRODUCTS
--------------------------------------------------
-- All products from single admin farmer (Green Valley Farm)
INSERT INTO product (farmer_id, category_id, unit_label_id, name, description, price_per_unit, stock_quantity, is_organic, is_active, image_url) VALUES
-- Vegetables
((SELECT id FROM farmer WHERE email = 'john@greenvalley.com'), (SELECT id FROM category WHERE name = 'Vegetables'), (SELECT id FROM unit_label WHERE name = 'lb'), 'Organic Tomatoes', 'Fresh, vine-ripened organic tomatoes. Perfect for salads, sandwiches, and cooking.', 4.50, 50.0, true, true, 'https://images.unsplash.com/photo-1546470427-227e9afa4855?w=300&q=80'),
((SELECT id FROM farmer WHERE email = 'john@greenvalley.com'), (SELECT id FROM category WHERE name = 'Vegetables'), (SELECT id FROM unit_label WHERE name = 'ear'), 'Sweet Corn', 'Sweet, tender corn on the cob, freshly harvested from our fields.', 0.75, 100.0, false, true, 'https://images.unsplash.com/photo-1551754655-cd27e38d2076?w=300&q=80'),
((SELECT id FROM farmer WHERE email = 'john@greenvalley.com'), (SELECT id FROM category WHERE name = 'Vegetables'), (SELECT id FROM unit_label WHERE name = 'lb'), 'Green Bell Peppers', 'Crisp and fresh green bell peppers, perfect for cooking and salads.', 3.99, 30.0, false, true, 'https://images.unsplash.com/photo-1563565375-f3fdfdbefa83?w=300&q=80'),
((SELECT id FROM farmer WHERE email = 'john@greenvalley.com'), (SELECT id FROM category WHERE name = 'Vegetables'), (SELECT id FROM unit_label WHERE name = 'head'), 'Organic Lettuce', 'Crisp organic lettuce, perfect for fresh salads and healthy meals.', 2.80, 30.0, true, true, 'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=300&q=80'),
((SELECT id FROM farmer WHERE email = 'john@greenvalley.com'), (SELECT id FROM category WHERE name = 'Vegetables'), (SELECT id FROM unit_label WHERE name = 'lb'), 'Organic Carrots', 'Sweet, crunchy organic carrots, great for snacking or cooking.', 3.20, 40.0, true, true, 'https://images.unsplash.com/photo-1445282768818-728615cc910a?w=300&q=80'),
((SELECT id FROM farmer WHERE email = 'john@greenvalley.com'), (SELECT id FROM category WHERE name = 'Vegetables'), (SELECT id FROM unit_label WHERE name = 'bag'), 'Mixed Greens', 'Fresh mixed greens including spinach, arugula, and baby lettuce.', 4.95, 20.0, true, true, 'https://images.unsplash.com/photo-1540420773420-3366772f4999?w=300&q=80'),
((SELECT id FROM farmer WHERE email = 'john@greenvalley.com'), (SELECT id FROM category WHERE name = 'Vegetables'), (SELECT id FROM unit_label WHERE name = 'bag'), 'Organic Spinach', 'Fresh organic spinach leaves, perfect for salads and cooking.', 3.75, 25.0, true, true, 'https://images.unsplash.com/photo-1576045057995-568f588f82fb?w=300&q=80'),
((SELECT id FROM farmer WHERE email = 'john@greenvalley.com'), (SELECT id FROM category WHERE name = 'Vegetables'), (SELECT id FROM unit_label WHERE name = 'lb'), 'Fresh Cucumbers', 'Crisp, fresh cucumbers perfect for salads and pickling.', 2.49, 45.0, false, true, 'https://images.unsplash.com/photo-1449300079323-02e209d9d3a6?w=300&q=80'),
((SELECT id FROM farmer WHERE email = 'john@greenvalley.com'), (SELECT id FROM category WHERE name = 'Vegetables'), (SELECT id FROM unit_label WHERE name = 'lb'), 'Yellow Squash', 'Tender yellow summer squash, great for grilling and cooking.', 3.29, 35.0, false, true, 'https://images.unsplash.com/photo-1518635297084-69ecb10cd8cc?w=300&q=80'),
((SELECT id FROM farmer WHERE email = 'john@greenvalley.com'), (SELECT id FROM category WHERE name = 'Vegetables'), (SELECT id FROM unit_label WHERE name = 'pint'), 'Cherry Tomatoes', 'Sweet cherry tomatoes, perfect for snacking and salads.', 3.49, 60.0, true, true, 'https://images.unsplash.com/photo-1592841200221-a6898f307baa?w=300&q=80'),
((SELECT id FROM farmer WHERE email = 'john@greenvalley.com'), (SELECT id FROM category WHERE name = 'Vegetables'), (SELECT id FROM unit_label WHERE name = 'bunch'), 'Organic Kale', 'Nutritious organic kale, perfect for smoothies and healthy cooking.', 2.99, 40.0, true, true, 'https://images.unsplash.com/photo-1515363578674-99719515ca13?w=300&q=80'),
-- Herbs
((SELECT id FROM farmer WHERE email = 'john@greenvalley.com'), (SELECT id FROM category WHERE name = 'Herbs'), (SELECT id FROM unit_label WHERE name = 'bunch'), 'Fresh Basil', 'Aromatic fresh basil, perfect for cooking and garnishing your favorite dishes.', 3.25, 25.0, true, true, 'https://images.unsplash.com/photo-1618164435735-413d3b066c9a?w=300&q=80'),
((SELECT id FROM farmer WHERE email = 'john@greenvalley.com'), (SELECT id FROM category WHERE name = 'Herbs'), (SELECT id FROM unit_label WHERE name = 'pack'), 'Fresh Herbs Mix', 'A variety pack of fresh herbs including parsley, cilantro, and dill.', 4.50, 15.0, false, true, 'https://images.unsplash.com/photo-1584308972272-9e4e7685e80f?w=300&q=80'),
-- Fruits
((SELECT id FROM farmer WHERE email = 'john@greenvalley.com'), (SELECT id FROM category WHERE name = 'Fruits'), (SELECT id FROM unit_label WHERE name = 'pint'), 'Strawberries', 'Sweet, juicy strawberries picked at peak ripeness.', 4.99, 50.0, true, true, 'https://images.unsplash.com/photo-1464965911861-746a04b4bca6?w=300&q=80'),
((SELECT id FROM farmer WHERE email = 'john@greenvalley.com'), (SELECT id FROM category WHERE name = 'Fruits'), (SELECT id FROM unit_label WHERE name = 'pint'), 'Blueberries', 'Fresh, antioxidant-rich blueberries perfect for snacking or baking.', 5.49, 30.0, true, true, 'https://images.unsplash.com/photo-1498557850523-fd3d118b962e?w=300&q=80');

--------------------------------------------------
-- ORDERS
--------------------------------------------------
-- Sample orders for testing (all from single admin farmer)
INSERT INTO orders (customer_id, farmer_id, status, payment_status, subtotal_amount, shipping_amount, total_amount, shipping_name, shipping_phone, shipping_address1, shipping_city, shipping_postal_code, shipping_country) VALUES
-- Alice's completed order
((SELECT id FROM customer WHERE email = 'alice@example.com'), (SELECT id FROM farmer WHERE email = 'john@greenvalley.com'), 'FULFILLED', 'CAPTURED', 12.25, 5.99, 18.24, 'Alice Johnson', '(555) 111-2222', '789 Main Street', 'Springfield', '62701', 'Israel'),
-- Bob's pending order
((SELECT id FROM customer WHERE email = 'bob@example.com'), (SELECT id FROM farmer WHERE email = 'john@greenvalley.com'), 'PAID', 'CAPTURED', 8.60, 5.99, 14.59, 'Bob Smith', '(555) 333-4444', '321 Oak Avenue', 'Springfield', '62703', 'Israel'),
-- Carol's order (now from admin farmer)
((SELECT id FROM customer WHERE email = 'carol@example.com'), (SELECT id FROM farmer WHERE email = 'john@greenvalley.com'), 'FULFILLED', 'CAPTURED', 15.40, 5.99, 21.39, 'Carol Davis', '(555) 555-6666', '456 Pine Street', 'Bloomington', '61701', 'Israel'),
-- David's pending order (now from admin farmer)
((SELECT id FROM customer WHERE email = 'david@example.com'), (SELECT id FROM farmer WHERE email = 'john@greenvalley.com'), 'PAID', 'CAPTURED', 7.98, 5.99, 13.97, 'David Wilson', '(555) 777-8888', '654 Elm Road', 'Champaign', '61820', 'Israel');

--------------------------------------------------
-- ORDER_ITEMS (Individual items within orders)
--------------------------------------------------
-- Alice's order items
INSERT INTO order_item (order_id, product_id, quantity, unit_price, line_subtotal, line_total) VALUES
((SELECT id FROM orders WHERE shipping_name = 'Alice Johnson'), (SELECT id FROM product WHERE name = 'Organic Tomatoes'), 2.0, 4.50, 9.00, 9.00),
((SELECT id FROM orders WHERE shipping_name = 'Alice Johnson'), (SELECT id FROM product WHERE name = 'Fresh Basil'), 1.0, 3.25, 3.25, 3.25);

-- Bob's order items
INSERT INTO order_item (order_id, product_id, quantity, unit_price, line_subtotal, line_total) VALUES
((SELECT id FROM orders WHERE shipping_name = 'Bob Smith'), (SELECT id FROM product WHERE name = 'Sweet Corn'), 8.0, 0.75, 6.00, 6.00),
((SELECT id FROM orders WHERE shipping_name = 'Bob Smith'), (SELECT id FROM product WHERE name = 'Green Bell Peppers'), 0.65, 3.99, 2.60, 2.60);

-- Carol's order items
INSERT INTO order_item (order_id, product_id, quantity, unit_price, line_subtotal, line_total) VALUES
((SELECT id FROM orders WHERE shipping_name = 'Carol Davis'), (SELECT id FROM product WHERE name = 'Organic Lettuce'), 2.0, 2.80, 5.60, 5.60),
((SELECT id FROM orders WHERE shipping_name = 'Carol Davis'), (SELECT id FROM product WHERE name = 'Mixed Greens'), 2.0, 4.95, 9.90, 9.90);

-- David's order items (using available products from admin farmer)
INSERT INTO order_item (order_id, product_id, quantity, unit_price, line_subtotal, line_total) VALUES
((SELECT id FROM orders WHERE shipping_name = 'David Wilson'), (SELECT id FROM product WHERE name = 'Fresh Cucumbers'), 2.0, 2.49, 4.98, 4.98),
((SELECT id FROM orders WHERE shipping_name = 'David Wilson'), (SELECT id FROM product WHERE name = 'Yellow Squash'), 1.0, 3.00, 3.00, 3.00);

--------------------------------------------------
-- SHIPMENTS
--------------------------------------------------
INSERT INTO shipment (order_id, status, tracking_number, shipped_at, delivered_at) VALUES
-- Alice's delivered shipment
((SELECT id FROM orders WHERE shipping_name = 'Alice Johnson'), 'DELIVERED', 'FARM-20241124-001', NOW() - INTERVAL '2 days', NOW() - INTERVAL '1 day'),
-- Bob's packed shipment
((SELECT id FROM orders WHERE shipping_name = 'Bob Smith'), 'PACKED', 'FARM-20241124-002', NULL, NULL),
-- Carol's delivered shipment
((SELECT id FROM orders WHERE shipping_name = 'Carol Davis'), 'DELIVERED', 'FARM-20241124-003', NOW() - INTERVAL '3 days', NOW() - INTERVAL '2 days'),
-- David's shipped shipment
((SELECT id FROM orders WHERE shipping_name = 'David Wilson'), 'SHIPPED', 'FARM-20241124-004', NOW() - INTERVAL '1 day', NULL);


--------------------------------------------------
-- SAMPLE SHOPPING CARTS
--------------------------------------------------
-- Active cart for Alice
INSERT INTO cart (session_id, customer_id, status) VALUES
('sample-session-alice-001', (SELECT id FROM customer WHERE email = 'alice@example.com'), 'ACTIVE');

-- Cart items for Alice's active cart
INSERT INTO cart_item (cart_id, product_id, quantity, unit_price) VALUES
((SELECT id FROM cart WHERE session_id = 'sample-session-alice-001'), (SELECT id FROM product WHERE name = 'Organic Tomatoes'), 1.0, 4.50),
((SELECT id FROM cart WHERE session_id = 'sample-session-alice-001'), (SELECT id FROM product WHERE name = 'Fresh Basil'), 2.0, 3.25);

-- Abandoned cart for Bob
INSERT INTO cart (session_id, customer_id, status) VALUES
('sample-session-bob-001', (SELECT id FROM customer WHERE email = 'bob@example.com'), 'ABANDONED');

INSERT INTO cart_item (cart_id, product_id, quantity, unit_price) VALUES
((SELECT id FROM cart WHERE session_id = 'sample-session-bob-001'), (SELECT id FROM product WHERE name = 'Sweet Corn'), 4.0, 0.75);

--------------------------------------------------
-- CUSTOMER SESSIONS
--------------------------------------------------
INSERT INTO customer_session (session_id, customer_id, user_type, is_active, last_activity) VALUES
('sample-session-alice-001', (SELECT id FROM customer WHERE email = 'alice@example.com'), 'CUSTOMER', true, NOW() - INTERVAL '1 hour'),
('sample-session-bob-001', (SELECT id FROM customer WHERE email = 'bob@example.com'), 'CUSTOMER', false, NOW() - INTERVAL '2 days'),
('sample-session-carol-001', (SELECT id FROM customer WHERE email = 'carol@example.com'), 'CUSTOMER', true, NOW() - INTERVAL '30 minutes'),
('sample-session-farmer-john', (SELECT id FROM farmer WHERE email = 'john@greenvalley.com'), 'FARMER', true, NOW() - INTERVAL '15 minutes');