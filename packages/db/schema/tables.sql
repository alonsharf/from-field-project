-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS pgcrypto;

--------------------------------------------------
-- ENUM TYPES
--------------------------------------------------
CREATE TYPE order_status AS ENUM (
    'DRAFT',            -- cart not yet submitted
    'PENDING_PAYMENT',
    'PAID',
    'CANCELLED',
    'FULFILLED'
);

CREATE TYPE payment_status AS ENUM (
    'NOT_REQUIRED',
    'PENDING',
    'AUTHORIZED',
    'CAPTURED',
    'FAILED',
    'REFUNDED'
);

CREATE TYPE shipment_status AS ENUM (
    'PENDING',      -- order paid, waiting to be packed
    'PACKED',
    'SHIPPED',
    'DELIVERED',
    'CANCELLED'
);

CREATE TYPE cart_status AS ENUM (
    'ACTIVE',
    'ABANDONED',
    'CONVERTED'
);

CREATE TYPE user_type AS ENUM (
    'FARMER',
    'CUSTOMER'
);

--------------------------------------------------
-- CATEGORY TABLE
--------------------------------------------------
CREATE TABLE category (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name            text NOT NULL UNIQUE,
    description     text,
    created_at      timestamptz NOT NULL DEFAULT now(),
    updated_at      timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_category_name ON category(name);

--------------------------------------------------
-- UNIT_LABEL TABLE
--------------------------------------------------
CREATE TABLE unit_label (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name            text NOT NULL UNIQUE,  -- e.g. 'kg', 'lb', 'bunch', 'pint', 'ear', 'head', 'bag', 'pack'
    abbreviation    text,                  -- e.g. 'kg', 'lb', 'pc'
    description     text,                  -- e.g. 'Kilogram', 'Pound', 'Per piece'
    created_at      timestamptz NOT NULL DEFAULT now(),
    updated_at      timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_unit_label_name ON unit_label(name);
CREATE INDEX idx_unit_label_abbreviation ON unit_label(abbreviation);

--------------------------------------------------
-- FARMER
--------------------------------------------------
CREATE TABLE farmer (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name                text        NOT NULL,       -- person name
    farm_name           text        NOT NULL,       -- brand name used in UI
    email               text        NOT NULL UNIQUE, -- unique for single farmer admin
    password_hash       text        NOT NULL,       -- bcrypt hashed password
    phone               text,
    address_line1       text,
    address_line2       text,
    city                text,
    postal_code         text,
    country             text DEFAULT 'Israel',
    is_active           boolean     NOT NULL DEFAULT true,

    -- Merged from farmer_profile table
    description         text,
    farm_type          text,                        -- 'Organic', 'Conventional', 'Hydroponic', etc.
    farm_size_acres    numeric(10,2),
    established_year   numeric(4,0),
    certifications     text,                        -- JSON string of certifications
    website            text,
    facebook_url       text,
    instagram_handle   text,
    twitter_handle     text,
    business_hours     text,
    profile_image_url  text,

    created_at          timestamptz NOT NULL DEFAULT now(),
    updated_at          timestamptz NOT NULL DEFAULT now()
);

--------------------------------------------------
-- CUSTOMER
--------------------------------------------------
CREATE TABLE customer (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    first_name          text        NOT NULL,
    last_name           text        NOT NULL,
    email               text        NOT NULL UNIQUE,
    password_hash       text        NOT NULL,       -- bcrypt hashed password
    phone               text,
    -- One main shipping address for now
    address_line1       text,
    address_line2       text,
    city                text,
    postal_code         text,
    country             text DEFAULT 'Israel',
    marketing_opt_in    boolean     NOT NULL DEFAULT false,
    created_at          timestamptz NOT NULL DEFAULT now(),
    updated_at          timestamptz NOT NULL DEFAULT now()
);

--------------------------------------------------
-- PRODUCT (belongs to a farmer, with FK to category and unit_label)
--------------------------------------------------
CREATE TABLE product (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    farmer_id           uuid        NOT NULL REFERENCES farmer(id),
    category_id         uuid        NOT NULL REFERENCES category(id),
    unit_label_id       uuid        NOT NULL REFERENCES unit_label(id),
    name                text        NOT NULL,
    description         text,
    unit_size           numeric(10,2), -- e.g. 1.00 kg, 0.5 kg, etc.
    price_per_unit      numeric(10,2) NOT NULL, -- price per unit_label
    currency            char(3) NOT NULL DEFAULT 'ILS',
    stock_quantity      numeric(12,2) NOT NULL DEFAULT 0,  -- current stock
    min_order_quantity  numeric(12,2) NOT NULL DEFAULT 1,
    max_order_quantity  numeric(12,2),     -- NULL = no limit
    is_active           boolean NOT NULL DEFAULT true,
    is_organic          boolean NOT NULL DEFAULT false,
    available_from      date,
    available_until     date,
    image_url           text,
    created_at          timestamptz NOT NULL DEFAULT now(),
    updated_at          timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_product_farmer_id ON product(farmer_id);
CREATE INDEX idx_product_category_id ON product(category_id);
CREATE INDEX idx_product_unit_label_id ON product(unit_label_id);
CREATE INDEX idx_product_is_active ON product(is_active);

--------------------------------------------------
-- ORDERS (linked to farmer + customer)
--------------------------------------------------
CREATE TABLE orders (
    id                      uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id             uuid        NOT NULL REFERENCES customer(id),
    farmer_id               uuid        NOT NULL REFERENCES farmer(id),

    status                  order_status    NOT NULL DEFAULT 'DRAFT',
    payment_status          payment_status  NOT NULL DEFAULT 'PENDING',
    payment_provider        text,           -- e.g. 'SIMULATED', 'PAYPAL'
    payment_reference       text,           -- external transaction id

    subtotal_amount         numeric(12,2) NOT NULL DEFAULT 0, -- sum of lines
    shipping_amount         numeric(12,2) NOT NULL DEFAULT 0,
    discount_amount         numeric(12,2) NOT NULL DEFAULT 0,
    total_amount            numeric(12,2) NOT NULL DEFAULT 0, -- subtotal + shipping - discounts
    currency                char(3) NOT NULL DEFAULT 'ILS',

    -- snapshot of shipping address at order time
    shipping_name           text,
    shipping_phone          text,
    shipping_address1       text,
    shipping_address2       text,
    shipping_city           text,
    shipping_postal_code    text,
    shipping_country        text DEFAULT 'Israel',

    customer_notes          text,
    internal_notes          text,           -- for farmer/backoffice only

    created_at              timestamptz NOT NULL DEFAULT now(),
    updated_at              timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_farmer_id   ON orders(farmer_id);
CREATE INDEX idx_orders_status      ON orders(status);
CREATE INDEX idx_orders_created_at  ON orders(created_at);

--------------------------------------------------
-- ORDER_ITEM (individual items within an order)
--------------------------------------------------
CREATE TABLE order_item (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id            uuid NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id          uuid NOT NULL REFERENCES product(id),
    quantity            numeric(12,2) NOT NULL CHECK (quantity > 0),
    unit_price          numeric(10,2) NOT NULL,   -- price per unit at time of order
    line_subtotal       numeric(12,2) NOT NULL,   -- quantity * unit_price
    line_discount       numeric(12,2) NOT NULL DEFAULT 0,
    line_total          numeric(12,2) NOT NULL,   -- line_subtotal - line_discount

    created_at          timestamptz NOT NULL DEFAULT now(),
    updated_at          timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_order_item_order_id   ON order_item(order_id);
CREATE INDEX idx_order_item_product_id ON order_item(product_id);

--------------------------------------------------
-- SHIPMENT (one shipment per order for now)
--------------------------------------------------
CREATE TABLE shipment (
    id                      uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id                uuid NOT NULL UNIQUE REFERENCES orders(id) ON DELETE CASCADE,
    status                  shipment_status NOT NULL DEFAULT 'PENDING',
    carrier_name            text,           -- e.g. 'FarmerVan', 'LocalCourier'
    tracking_number         text,
    estimated_delivery_date date,
    shipped_at              timestamptz,
    delivered_at            timestamptz,

    -- optional override of address (if different from order)
    shipping_name           text,
    shipping_phone          text,
    shipping_address1       text,
    shipping_address2       text,
    shipping_city           text,
    shipping_postal_code    text,
    shipping_country        text,

    created_at              timestamptz NOT NULL DEFAULT now(),
    updated_at              timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_shipment_order_id ON shipment(order_id);
CREATE INDEX idx_shipment_status   ON shipment(status);

--------------------------------------------------
-- CUSTOMER SESSION (for Streamlit app)
--------------------------------------------------
CREATE TABLE customer_session (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id      text NOT NULL UNIQUE,
    customer_id     uuid REFERENCES customer(id),
    user_type       user_type NOT NULL DEFAULT 'CUSTOMER',
    is_active       boolean NOT NULL DEFAULT true,
    last_activity   timestamptz NOT NULL DEFAULT now(),
    created_at      timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_customer_session_session_id ON customer_session(session_id);
CREATE INDEX idx_customer_session_customer_id ON customer_session(customer_id);
CREATE INDEX idx_customer_session_last_activity ON customer_session(last_activity);

--------------------------------------------------
-- CART (shopping cart)
--------------------------------------------------
CREATE TABLE cart (
    id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id  text NOT NULL,  -- For anonymous carts
    customer_id uuid REFERENCES customer(id),
    status      cart_status NOT NULL DEFAULT 'ACTIVE',
    created_at  timestamptz NOT NULL DEFAULT now(),
    updated_at  timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_cart_session_id ON cart(session_id);
CREATE INDEX idx_cart_customer_id ON cart(customer_id);
CREATE INDEX idx_cart_status ON cart(status);

--------------------------------------------------
-- CART ITEM (items in shopping cart)
--------------------------------------------------
CREATE TABLE cart_item (
    id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    cart_id     uuid NOT NULL REFERENCES cart(id) ON DELETE CASCADE,
    product_id  uuid NOT NULL REFERENCES product(id),
    quantity    numeric(12,2) NOT NULL CHECK (quantity > 0),
    unit_price  numeric(10,2) NOT NULL,  -- Price at time of adding to cart
    created_at  timestamptz NOT NULL DEFAULT now(),
    updated_at  timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_cart_item_cart_id ON cart_item(cart_id);
CREATE INDEX idx_cart_item_product_id ON cart_item(product_id);


