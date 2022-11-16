import pandas as pd
import numpy as np

df = pd.read_pickle("data/chicago_animals.pkl")

df = df.drop(['id', 'organization_id', 'url','type','species', 'name', 'description','contact', '_links'], axis=1)

# explode the breeds column
df_breeds = df["breeds"].apply(pd.Series)
df_breeds.columns = [f"breed_{col}" for col in df_breeds.columns]
df = pd.concat([df.drop(["breeds"], axis=1), df_breeds], axis=1)

# explode the color column
df_colors = df["colors"].apply(pd.Series)
df_colors.columns = [f"colors_{col}" for col in df_colors.columns]
df = pd.concat([df.drop(["colors"], axis=1), df_colors], axis=1)

# explode the attribute column
df_attributes = df["attributes"].apply(pd.Series)
df_attributes.columns = [f"attribute_{col}" for col in df_attributes.columns]
df = pd.concat([df.drop(["attributes"], axis=1), df_attributes], axis=1)

# explode the environment column
df_environment = df["environment"].apply(pd.Series)
df_environment.columns = [f"env_{col}" for col in df_environment.columns]
df = pd.concat([df.drop(["environment"], axis=1), df_environment], axis=1)

# additional fields that need to be dropped after exploding columns
df = df.drop(['attribute_declawed','breed_unknown'], axis=1)

# mapping age and size
age_dict={
'Baby':'0',
'Young':'1',
'Adult':'2',
'Senior':'3'
}
df['age'] = df['age'].map(age_dict).astype(str).astype(int)

size_dict={
'Small':'0',
'Medium':'1',
'Large': '2',
'Extra Large': '3'
}
df['size'] = df['size'].map(size_dict).astype(str).astype(int)

# True/false conversions
df["organization_animal_id"] = df["organization_animal_id"].astype(bool).astype(int)
df["photos"] = df["photos"].astype(bool).astype(int)
df["primary_photo_cropped"] = df["primary_photo_cropped"].astype(bool).astype(int)
df["videos"] = df["videos"].astype(bool).astype(int)
df["status"] = df["status"].astype(bool).astype(int)
df["breed_mixed"] = df["breed_mixed"].astype(int)
df["attribute_spayed_neutered"] = df["attribute_spayed_neutered"].astype(int)
df["attribute_house_trained"] = df["attribute_house_trained"].astype(int)
df["attribute_special_needs"] = df["attribute_special_needs"].astype(int)
df["attribute_shots_current"] = df["attribute_shots_current"].astype(int)
df["env_children"] = df["env_children"].astype(bool).astype(int)
df["env_dogs"] = df["env_dogs"].astype(bool).astype(int)
df["env_cats"] = df["env_cats"].astype(bool).astype(int)
df["env_children"] = df["env_children"].astype(bool).astype(int)
df["env_dogs"] = df["env_dogs"].astype(bool).astype(int)
df["env_cats"] = df["env_cats"].astype(bool).astype(int)

# One hot encoding categorical variables
df = pd.get_dummies(df, columns =["gender","coat","colors_primary","colors_secondary","colors_tertiary"])