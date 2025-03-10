# Execute in the scripts folder
cd ..
./.venv/Scripts/activate
python consultant_info_generator/cli/main.py import-consultants-with-categories-file -f data/profiles.txt --remove-existing
cd scripts
