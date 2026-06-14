from services.data_store import save_data
from services.stats_service import update_all_data

if __name__ == "__main__":
    data = update_all_data()
    save_data(data)
    print("Datos actualizados")
    print(data.get("metadata", {}))
