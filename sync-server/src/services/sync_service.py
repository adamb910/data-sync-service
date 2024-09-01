
# Could extend with strategy pattern to allow different implementations
class SyncService():
    
    def push_update(self, updated_batch):
        print("SyncService.push_update")

    def get_batches_since_datetime(self, datetime):
        print("SyncService.get_batches_since_datetime")
