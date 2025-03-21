from consultant_info_generator.model.category import Category


def create_dummy_category() -> Category:
    return Category(
        name="Industry",
        description="This is the industry in which the consultant operates",  #
        list_of_values=[
            "Cars",
            "Automotive",
            "Automotive Industry",
            "Civil Engineering",
            "Consulting",
            "Consulting Industry",
            "Energy",
            "Finance",
            "Insurance",
            "IT",
            "Other",
        ],
    )
