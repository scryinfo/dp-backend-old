CREATE TABLE scry2.category_tree  (
  id serial primary key,
  parent_id int REFERENCES scry2.category_tree,
  name text,
  created_at timestamp  DEFAULT now()
);


CREATE OR REPLACE FUNCTION scry2.category_verify_name() RETURNS trigger AS $category_verify_name$
    DECLARE cat_name  text;
    BEGIN
        -- Check that empname and salary are given
        IF NEW.parent_id IS NOT NULL THEN
          SELECT name
          INTO cat_name
          FROM scry2.category_tree
          WHERE parent_id = NEW.parent_id and name=NEW.name;
        ELSE
          SELECT name
          INTO cat_name
          FROM scry2.category_tree
          WHERE parent_id IS NULL and name=NEW.name;

        END IF;

        IF cat_name IS NOT NULL THEN
            RAISE EXCEPTION 'Name exists for this parent_id';
        END IF;


        RETURN NEW;
    END;
$category_verify_name$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS category_verify_name ON scry2.category_tree;

CREATE TRIGGER category_verify_name BEFORE INSERT OR UPDATE ON scry2.category_tree
    FOR EACH ROW EXECUTE PROCEDURE scry2.category_verify_name();


INSERT INTO scry2.category_tree (name) VALUES('Aviation');

INSERT INTO scry2.category_tree (name, parent_id) VALUES('Commercial',1);

INSERT INTO scry2.category_tree (name, parent_id) VALUES('Private',1);

INSERT INTO scry2.category_tree (name, parent_id) VALUES('Airport',2);


INSERT INTO scry2.category_tree (name, parent_id) VALUES('ROOT',4);
