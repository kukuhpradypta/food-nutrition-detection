---
license: cc
task_categories:
- image-classification
- feature-extraction
- zero-shot-classification
size_categories:
- 1K<n<10K
---

# Food Nutrients: A Macronutrients Dataset

`food_nutrients` is a dataset of visual and nutritional data for ~3k realistic plates of food captured from Google cafeterias using a custom scanning rig.

This dataset provides annotated pictures of food plates along with **calories**, **macronutrients** (fat, carbohydrate, protein) for the total plate and **for every ingredient** as well.
![image/jpeg](https://cdn-uploads.huggingface.co/production/uploads/643803191ee0e43f14d6c073/bIy0hkka3XyXKBKebn8kI.jpeg)

| Column           | Definition                                                                                                     |
|------------------|----------------------------------------------------------------------------------------------------------------|
| `image`          | a 640x640 top-down image from a realistic food plate in the Google cafeteria                                   |
| `id`             | identifier of the sample                                                                                       |
| `split`          | the split of the sample, only `test` for now                                                                   |
| `ingredients`    | a list of the different ingredients, with the mass (`grams`), `calories`, `fat`, `carb`, `protein` and `name`. |
| `total_mass`     | total calories of the plate                                                                                    |
| `total_calories` | the total mass of the food on the plate                                                                        |
| `total_fat`      | the total fat on the plate                                                                                     |
| `total_carb`     | total carbohydrates on the plate                                                                               |
| `total_protein`  | total protein on the plate                                                                                     |

## Source

This data was taken from Google Research's dataset [Nutrition5k](https://github.com/google-research-datasets/Nutrition5k). It's cleaned up and filtered, because this dataset had many issues such as missing images or missing calorie information for certain samples. That's why this dataset is a bit smaller than 5k samples.

## Run Migration
alembic upgrade head

## Rollback Migration
alembic downgrade base