from setup_utils import create_driver, login_to_joomla, auto_create_driver
from metadata_creator import metadata_description_editor, process_metadata_for_events_in_articles, process_metadata_for_activities, process_metadata_for_what_to_do, change_menu_name, change_menu_names_for_countries

# driver = create_driver()
driver = auto_create_driver()
login_to_joomla(driver)
input("Press Enter to continue...")

countries = [
    "Japan",
    "Jordan",
    "Laos",
    "Latvia",
    "Lebanon",
    "Lithuania",
    "Malaysia",
    "Maldives",
    "Malta",
    "Mauritius",
    "Mexico",
    "Monaco",
    "Montenegro",
    "Mozambique",
    "Myanmar",
    "the Netherlands",
    "Peru",
    "Poland",
    "Portugal",
    "Reunion",
    "Rwanda",
    "Scotland",
    "Senegal",
    "Serbia",
    "Singapore",
    "Slovenia",
    "South Korea",
    "Sri Lanka",
    "Sweden",
    "Switzerland",
    "Taiwan",
    "Thailand",
    "Tunisia",
    "Uganda",
    "the United Kingdom",
    "Uzbekistan",
    "Venezuela",
    "Vietnam",
    "Zanzibar",
]

# change_menu_names_for_countries(driver, countries)


