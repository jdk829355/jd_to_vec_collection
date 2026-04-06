from prefect import task, flow

@task(name="collect data")
def collect_data():
    print("data collected!")

@flow(name="data collection pipeline")
def data_collection_pipeline():
    collect_data()