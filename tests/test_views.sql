-- Test file for view naming rules

-- View with incorrect naming (violates VW01)
CREATE OR REPLACE VIEW public.user_details AS
SELECT
    users.id,
    users.name,
    users.email,
    addresses.street,
    addresses.city
FROM
    public.users
JOIN
    public.addresses ON users.id = addresses.user_id;

-- View with correct naming (does not violate VW01)
CREATE OR REPLACE VIEW public.v_user_details AS
SELECT
    users.id,
    users.name,
    users.email,
    addresses.street,
    addresses.city
FROM
    public.users
JOIN
    public.addresses ON users.id = addresses.user_id;
