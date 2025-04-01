-- Test file for constraint naming rules

-- Primary key constraint with incorrect naming (violates CR01)
CREATE TABLE public.person (
    person_id INT,
    CONSTRAINT person_pk PRIMARY KEY (person_id)
);

-- Foreign key constraint with incorrect naming (violates CR02)
CREATE TABLE public.orders (
    order_id INT,
    person_id INT,
    CONSTRAINT orders_person_fk FOREIGN KEY (person_id) REFERENCES public.person (person_id)
);

-- Check constraint with incorrect naming (violates CR03)
CREATE TABLE public.product (
    product_id INT,
    price DECIMAL(10, 2),
    CONSTRAINT price_positive CHECK (price > 0)
);

-- Unique constraint with incorrect naming (violates CR04)
CREATE TABLE public.customer (
    customer_id INT,
    email VARCHAR(255),
    CONSTRAINT email_unique UNIQUE (email)
);

-- Default constraint with incorrect naming (violates CR05)
-- Note: PostgreSQL doesn't support CONSTRAINT for DEFAULT values
-- using ALTER TABLE instead
CREATE TABLE public.employee (
    employee_id INT,
    is_active BOOLEAN DEFAULT FALSE
);

ALTER TABLE public.employee
ALTER COLUMN is_active SET DEFAULT TRUE;
