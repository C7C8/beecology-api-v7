-- Utility stuff
-- CREATE EXTENSION "postgis";
-- CREATE EXTENSION "uuid-ossp";
ALTER TABLE public.bee_flower_observation ALTER COLUMN id SET DEFAULT uuid_generate_v4();
ALTER TABLE public.flower_species ALTER COLUMN id SET DEFAULT uuid_generate_v4();
ALTER TABLE public.bee_species ALTER COLUMN id SET DEFAULT uuid_generate_v4();
ALTER TABLE public.media ALTER COLUMN id SET DEFAULT uuid_generate_v4();
ALTER TABLE public.news ALTER COLUMN id SET DEFAULT uuid_generate_v4();

CREATE OR REPLACE FUNCTION month_abbrv_to_name(abbr varchar)
RETURNS months AS $month$
    BEGIN
        RETURN CASE
            WHEN abbr = 'Jan' THEN 'January'
            WHEN abbr = 'Feb' THEN 'February'
            WHEN abbr = 'Mar' THEN 'March'
            WHEN abbr = 'May' THEN abbr
            WHEN abbr = 'Jun' THEN 'June'
            WHEN abbr = 'Jul' THEN 'July'
            WHEN abbr = 'Aug' THEN 'August'
            WHEN abbr = 'Sep' THEN 'September'
            WHEN abbr = 'Oct' THEN 'October'
            WHEN abbr = 'Nov' THEN 'November'
            WHEN abbr = 'Dec' THEN 'December'
        END;
    END
$month$ LANGUAGE plpgsql;

-- Create user entries
INSERT INTO public."user" (id)
    SELECT DISTINCT "user_id" FROM orig.beerecord;
UPDATE public."user" SET admin = (public."user".id IN (SELECT user_id FROM orig.admintable)),
                         locked = FALSE,
                         registration_date = now();

-- Create flower_species entries, with a holdover orig_id field to assist in bee record linking later
ALTER TABLE flower_species ADD COLUMN orig_id INT;
INSERT INTO flower_species (genus, species, common_name, alt_names, main_color, colors, bloom_start, bloom_end, shape, image, orig_id)
    SELECT lower(split_part(latin_name, ' ', 1)), split_part(latin_name, ' ', 2), --Genus+species split
           lower(main_common_name),
           lower(string_to_array(common_name, ', ')::text)::text[],
           lower(main_color),
           lower(string_to_array(colors, ',')::text)::text[],
           month_abbrv_to_name(split_part(bloom_time, ',', 1)), -- Start month
           month_abbrv_to_name(split_part(bloom_time, ',', array_length(string_to_array(bloom_time, ','), 1))), -- End month
           shape,
           image_src,
           flower_id
    FROM orig.flowerdict;

-- Create bee_species entries, with holdover orig_id field to assist in bee record linking later
ALTER TABLE bee_species ADD COLUMN IF NOT EXISTS orig_id INT;
INSERT INTO bee_species (species, common_names, description, active_start, active_end, confused_with, image, orig_id)
    SELECT lower(split_part(bee_name, ' ', 2)),
           string_to_array(common_name, ','), -- Basically does nothing, just convert to an array
           description,
           split_part(active_months, ' - ', 1)::months,
           split_part(active_months, ' - ', 2)::months,
           string_to_array(confused, ', '),
           bee_pic_path,
           bee_id
    FROM orig.beedict;

-- Create media entries for images
INSERT INTO media (user_id, web_path, file_path, type, uploaded)
    SELECT user_id,
           record_pic_path AS web_path,
           '/datastoreage/' || record_pic_path AS file_path, -- not a typo
           'image' AS type,
           time
    FROM orig.beerecord
    WHERE record_pic_path IS NOT NULL;

-- Create media entries for videos
INSERT INTO media (user_id, web_path, file_path, type, uploaded)
    SELECT user_id,
           record_video_path AS web_path,
           '/datastoreage/' || record_video_path AS file_path, -- not a typo
           'video' AS type,
           time
    FROM orig.beerecord
    WHERE record_video_path IS NOT NULL;

-- Create bee record entries
ALTER TABLE bee_flower_observation ADD COLUMN temp_video_path VARCHAR;
ALTER TABLE bee_flower_observation ADD COLUMN temp_img_path VARCHAR;
INSERT INTO bee_flower_observation (abdomen_coloration, thorax_coloration, head_coloration, gender, behavior, time, submitted, location, elevation, closest_city, how_submitted, user_id, flower_species_id, bee_species_id, temp_img_path, temp_video_path)
    SELECT coloration_abdomen,
           coloration_thorax,
           coloration_head,
           gender::bee_gender,
           bee_behavior::bee_behavior,
           time,
           time,
           CASE
               WHEN loc_info = 'undefined' OR loc_info = ''  OR loc_info = ',' THEN null
               ELSE 'POINT(' || regexp_replace(loc_info, ',', ' ') || ')'
            END AS location,
           CASE
               WHEN elevation = '' THEN NULL
               ELSE elevation::float
           END AS elevation,
           CASE
               WHEN city_name = 'undefined' THEN NULL
               else city_name
           END AS closest_city,
           CASE
               WHEN user_id = 'historical@edu.com' THEN 'museum'::submission_type
               WHEN record_video_path IS NOT NULL THEN 'androidapp'::submission_type
               ELSE 'webapp'::submission_type
           END,
           user_id,
           flower_species.id AS flower_species_id,
           bee_species.id AS bee_species_id,
           record_pic_path,
           record_video_path
    FROM orig.beerecord
    LEFT JOIN bee_species ON orig.beerecord.bee_dict_id = bee_species.orig_id
    LEFT JOIN flower_species ON lower(flower_species.genus || ' ' || flower_species.species) = lower(orig.beerecord.flower_name);

-- Link media entries to bee record
UPDATE media SET bee_flower_observation_id = (SELECT id FROM bee_flower_observation WHERE media.web_path = temp_img_path) WHERE type = 'image';
UPDATE media SET bee_flower_observation_id = (SELECT id FROM bee_flower_observation WHERE media.web_path = temp_video_path) WHERE type = 'video';

-- Clean up temp columns
ALTER TABLE bee_species DROP COLUMN orig_id;
ALTER TABLE flower_species DROP COLUMN orig_id;
ALTER TABLE bee_flower_observation DROP COLUMN temp_img_path;
ALTER TABLE bee_flower_observation DROP COLUMN temp_video_path
