from consultant_info_generator.model.category import Category

def create_dummy_category():
    return Category(name="Industry", description="This is the industry in which some operates", #
                    list_of_values=["Cars", "Civil Engineering", "Consulting", "Energy", "Finance", "Insurance", "IT", "Other"])

