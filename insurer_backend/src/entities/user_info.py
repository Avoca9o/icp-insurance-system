class UserInfo:
    def __init__(self, phone, payout_address, insurer, secondary_filters, schema):
        self.phone = phone
        self.payout_address = payout_address
        self.insurer = insurer
        self.secondary_filters = secondary_filters
        self.schema = schema
