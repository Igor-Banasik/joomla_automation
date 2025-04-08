from setup_utils import create_driver, login_to_joomla
from metadata_creator import metadata_description_editor, process_metadata_for_events_in_articles, process_metadata_for_activities, process_metadata_for_what_to_do

driver = create_driver()
login_to_joomla(driver)

countries = [
    "Italy",
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

process_metadata_for_what_to_do(driver, countries)


