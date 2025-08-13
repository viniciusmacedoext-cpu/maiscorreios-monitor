from datetime import datetime
import pytz

# Timezone do Brasil (São Paulo)
BRAZIL_TZ = pytz.timezone('America/Sao_Paulo')

def get_brazil_time():
    """Retorna a data e hora atual no timezone do Brasil"""
    return datetime.now(BRAZIL_TZ)

def format_brazil_time(dt=None, format_str='%Y-%m-%d %H:%M:%S'):
    """Formata uma data/hora para o timezone do Brasil"""
    if dt is None:
        dt = get_brazil_time()
    elif dt.tzinfo is None:
        # Se não tem timezone, assume UTC e converte para Brasil
        dt = pytz.utc.localize(dt).astimezone(BRAZIL_TZ)
    else:
        # Se já tem timezone, converte para Brasil
        dt = dt.astimezone(BRAZIL_TZ)
    
    return dt.strftime(format_str)

def get_brazil_datetime_for_db():
    """Retorna datetime para salvar no banco (sem timezone)"""
    return get_brazil_time().replace(tzinfo=None)
