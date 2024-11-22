from modules.alarms import get_temp_alarms
from modules.models import get_predictions
from modules.segment import get_temperatures, define_otsu_masks, reshape_img, get_region_size
from modules.data import get_last_image, get_masks, append_timeseries, save_alarms_table
import sys
import importlib

if __name__ == '__main__':

    cfgFile = sys.argv[1] if len(sys.argv) > 1 else 'config'
    cfg = importlib.import_module(cfgFile)
    alarms = False

    # Cargamos la última imagen disponible y las máscaras:
    image, timestamp = get_last_image(cfg.images_folder, cfg.camera_filter, cfg.images_folder_filter)
    masks = get_masks(cfg.masks_folder)
    print('Obtenida imagen:', timestamp)

    # Extraemos la temperatura media de cada región y almacenamos en el histórico:
    temperatures = get_temperatures(image, [timestamp], masks)
    append_timeseries(temperatures, cfg.temperatures_folder)
    print('Obtenidos valores de temperatura reales.')

    # Cargargamos las predicciones para este instante temporal:
    predicted = get_predictions(timestamp, temperatures, cfg.predictions)
    append_timeseries(predicted, cfg.predicted_folder)
    print('Obtenidos valores de temperatura predichos.')
    
    # Calculamos las máscaras de la imagen actual y almacenamos
    # el tamaño de cada región:
    # image_ = reshape_img(image, cfg.height, cfg.width)
    # masks_ = define_otsu_masks(image_, cfg.otsu_levels, cfg.compute_mser)
    # regions_size = get_region_size(masks_, timestamp)
    # append_timeseries(regions_size, cfg.regions_folder)

    # Calculamos las alarmas en función de las predicciones
    alarms, F = get_temp_alarms(temperatures, predicted, cfg.predictions)
    append_timeseries(alarms, cfg.alarms_folder)
    append_timeseries(F, cfg.f_value_folder)
    print('Generadas las alarmas.')
        
    # Almacenamos una tabla con las alarmas actuales para enviar a Gridwatch
    # a través de la API de ATIS:
    alarms_sent = save_alarms_table(alarms, predicted, temperatures, cfg)
    append_timeseries(alarms_sent, cfg.alarms_sent_folder)
