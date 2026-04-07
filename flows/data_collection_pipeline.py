from prefect import task, flow

@task(name="collect data")
def collect_data():
    print("data collected!")

@task(name="insert to db")
def insert_to_db(announcements):
    print("data collected!")

@flow(name="data collection pipeline")
def data_collection_pipeline():
    collect_data()

if __name__ == "__main__":
    data_collection_pipeline()