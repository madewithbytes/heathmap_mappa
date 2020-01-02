import os


def get_true_values_from_string(value):
    true_values = ["1", "true", "on"]
    return value.lower() in true_values


DEBUG = get_true_values_from_string(os.getenv('DEBUG', 'false'))

STATES = (
    'Oaxaca',
    'Puebla',
    'Veracruz',
    'Mexico',
    'Jalisco',
    'Chiapas',
    'Michoacan',
    'Yucatan',
    'Hidalgo',
    'Guerrero',
    'Sonora',
    'Chihuahua',
    'Tlaxcala',
    'San Luis Potosi',
    'Zacatecas',
    'Nuevo Leon',
    'Guanajuato',
    'Tamaulipas',
    'Coahuila',
    'Durango',
    'Morelos',
    'Nayarit',
    'Sinaloa',
    'Queretaro',
    'Tabasco',
    'Distrito Federal',
    'Aguascalientes',
    'Quintana Roo',
    'Campeche',
    'Colima',
    'Baja California',
    'Baja California Sur',
)


def normalize_state_name(state):
    """Ensures capitalisation of the state name matches SHP file."""
    for s in STATES:
        if s.lower() == state.lower():
            return s
    raise ValueError('Unknown state: `{}`'.format(state))
