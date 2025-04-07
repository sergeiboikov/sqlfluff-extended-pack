-- Test file for function naming rules

-- Function with incorrect naming (violates FN01)
CREATE OR REPLACE FUNCTION public.get_user_by_id(p_user_id INT)
RETURNS TABLE (
    id INT,
    name TEXT,
    email TEXT
)
LANGUAGE sql
AS $$
    SELECT id, name, email FROM users WHERE id = user_id
$$;

-- Function with correct naming (does not violate FN01)
CREATE OR REPLACE FUNCTION public.fun_get_user_by_id(user_id INT)
RETURNS TABLE (
    id INT,
    name TEXT,
    email TEXT
)
LANGUAGE sql
AS $$
    SELECT id, name, email FROM users WHERE id = user_id
$$;
