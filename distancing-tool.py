import populartimes
import googlemaps
import datetime
import config

# Pull API key from config file and instantiate client
KEY = config.key
CLIENT = googlemaps.Client(KEY)

# Day list for easy conversion by weekday index
DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday",
        "Thursday", "Friday", "Saturday"]


class Place:

    def __init__(self, place_id, name, address, coordinates, types, popularity,
                 rating, rating_n):
        self.place_id = place_id
        self.name = name
        self.address = address
        self.coordinates = coordinates
        self.types = types
        self.popularity = fix_popularity(popularity)
        self.rating = rating
        self.rating_n = rating_n

    def __str__(self):
        """
        Returns string version of a constructor call with the present attributes

        :return: String of attributes
        """
        attributes = vars(self).keys()
        n_attributes = len(attributes)
        header = "Place("

        for i in range(n_attributes):
            if i != n_attributes - 1:
                header += "{},"
            else:
                header += "{})"

        arguments = []
        for att in attributes:
            arg = getattr(self, att)
            if type(arg) == str:
                arguments.append("\"" + arg + "\"")
            else:
                arguments.append(arg)

        return header.format(*arguments)

    def find_best_time(self):
        """
        Returns the single least popular hour of the week

        :return: Tuple with two values: day number, {hour: popularity}
        """
        popularities = self.find_best_times_week()

        # Find the first day of the week that's open, starting with Sunday (0)
        d = 0
        while len(popularities[d]) == 0:
            d += 1

        # Initialize lowest vars with data from the first open day
        lowest_day = d
        lowest_hr = list(popularities[d])[0]
        lowest_pop = list(popularities[d].values())[0]

        # Compare all subsequent days with the lowest day
        for day in range(d + 1, len(popularities)):
            if len(popularities[day]) == 0:
                continue
            # Trust me, there's not another way to write this line
            pop = list(popularities[day].values())[0]
            if pop < lowest_pop:
                lowest_pop = pop
                lowest_day = day

        return lowest_day, {lowest_hr: lowest_pop}

    def find_best_times_week(self, n=1):
        """
        Returns the least popular n hours for each day of the week

        :param n: The number of times per day desired
        :return: List of dictionaries with hour:popularity pairs
        """
        best_times = []

        # Find the best n times for each day
        for day in range(len(self.popularity)):
            popularities = self.find_best_times_today(day=day, n=n)
            best_times.append(popularities)

        return best_times

    def find_best_times_today(self, day, n=1):
        """
        Returns the n least popular hours on the given day. If no day is given,
        the current day is used.

        :param day: Week day int, e.g Wednesday is 3
        :param n: The number of times desired
        :return: Dictionary with n hour: popularity pairs
        """
        # Get current datetime information
        if day is None:
            dt = datetime.datetime.now()
            day = dt.weekday()

        popularities = self.popularity[day]["data"]

        # Remove closed hours and sort by popularity (increasing)
        popularities = {key: val for key, val in popularities.items()
                        if val != 0}
        popularities = {k: v for k, v in sorted(popularities.items(),
                                                key=lambda x: x[1])}

        best_times = {}

        for key in list(popularities)[:n]:
            best_times[key] = popularities[key]

        return best_times


def get_place(query: str):
    """
    Takes a search query string and returns a Place object populated with
    results of a populartimes.get request. The search query can be any kind
    of Place data, like a name or address.

    :param query: The text input specifying which place to search for
    :return: Place object
    """

    # Establish ~10 mile circular search bias around the Eugene area
    bias = "circle:16100@44.050505,-123.095051"
    # Get place ID from a given search query using Places API
    search = CLIENT.find_place(query, "textquery", location_bias=bias)
    place_id = search["candidates"][0]["place_id"]

    # Get place details using the populartimes library
    info = populartimes.get_id(KEY, place_id)
    place = Place(place_id, info["name"], info["address"], info["coordinates"],
                  info["types"], info["populartimes"], info["rating"],
                  info["rating_n"])

    return place


def get_sample_place():
    """
    Returns a sample Place object to avoid extraneous API calls. The example is
    a Trader Joe's in Eugene, OR.

    :return: Place object
    """
    sample = Place("ChIJKwYiKvzhwFQRbQAN2nAbtkI", "Trader Joe's",
                   "85 Oakway Center, Eugene, OR 97401, USA",
                   {'lat': 44.0662723, 'lng': -123.0752647},
                   [
                       'grocery_or_supermarket', 'florist', 'supermarket',
                       'liquor_store', 'food', 'health', 'point_of_interest',
                       'store', 'establishment'
                   ],
                   [
                       {'name': 'Monday',
                        'data': [0, 0, 0, 0, 0, 0, 0, 0, 0, 22, 37, 53, 61, 61,
                                 58, 61, 72, 78, 68, 0, 0, 0, 0, 0]},
                       {'name': 'Tuesday',
                        'data': [0, 0, 0, 0, 0, 0, 0, 0, 0, 31, 45, 58, 64, 61,
                                 53, 46, 47, 52, 48, 0, 0, 0, 0, 0]},
                       {'name': 'Wednesday',
                        'data': [0, 0, 0, 0, 0, 0, 0, 0, 0, 23, 30, 36, 39, 44,
                                 57, 51, 34, 30, 0, 0, 0, 0, 0]},
                       {'name': 'Thursday',
                        'data': [0, 0, 0, 0, 0, 0, 0, 0, 0, 24, 36, 46, 54, 55,
                                 53, 49, 48, 45, 38, 0, 0, 0, 0, 0]},
                       {'name': 'Friday',
                        'data': [0, 0, 0, 0, 0, 0, 0, 0, 0, 37, 50, 59, 63, 62,
                                 59, 58, 59, 57, 46, 0, 0, 0, 0, 0]},
                       {'name': 'Saturday',
                        'data': [0, 0, 0, 0, 0, 0, 0, 0, 0, 38, 56, 72, 83, 88,
                                 88, 86, 82, 68, 45, 0, 0, 0, 0, 0]},
                       {'name': 'Sunday',
                        'data': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                 0, 0, 0, 0, 0, 0, 0, 0]}
                   ],
                   4.5,
                   1003)

    return sample


def fix_popularity(popularity: list):
    """
    Refactors popularity information returned by populartimes to be more
    easily usable.

    :param popularity: List of dictionaries returned by populartimes library
    :return: List of dictionaries
    """
    # Move Sunday to index 0 to match the ordering used in datetime
    popularity = popularity[-1:] + popularity[:-1]

    # Change popularity to a dictionary of hour: popularity pairs
    for day in popularity:
        vals = day["data"]
        day["data"] = {}
        for hour in range(len(vals)):
            day["data"][hour] = vals[hour]

    return popularity


def format_time(hour, day=None):
    """
    Takes an hour and day number and converts them to a formatted string

    :return: String in day, hour format
    """
    time = ""
    if day is not None:
        time += DAYS[day] + ", "

    dt = datetime.time(hour=hour)
    # Windows uses #, Unix uses -
    try:
        time += dt.strftime("%#I%p")
    except:
        time += dt.strftime("%-I%p")

    return time


def main():
    print("Find the least popular time to visit a place. Searches biased to Eugene")
    print("Use \"test\" to use the sample query, " + "\"trader joes\", with no API call")

    while True:
        user_in = input("Enter search query: ").strip().lower()
        if user_in == "test":
            place = get_sample_place()
        else:
            try:
                place = get_place(user_in)
            except:
                print("Unable to find popularity data for", user_in)
                continue

        best_times = place.find_best_time()
        day = best_times[0]
        hour = list(best_times[1].keys())[0]

        print("The least popular time to visit", place.name, "is", format_time(hour, day))


if __name__ == "__main__":
    main()
