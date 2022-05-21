from django_extensions.management.jobs import HourlyJob


class Job(HourlyJob):
    help = "Move all materials from ShelvingCart after X (configurable) hours."

    def execute(self):
        # TODO: Load and execute all configs here
        #
        # check if cloudconfigs folder exists
        # load all configs
        # check for check_in.use_shelving_cart
        # find hourly delay
        # pull all materials for all hosts that are in the shelving cart
        # compare updated_at + hourly delay to current time for each host
        # if current time > updated_at + hourly delay, remove shelving cart checkout
        # save

        pass
