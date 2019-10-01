import requests
import pytest
import json
import random
import string

def _url(path):
    return 'https://automationintesting.online/' + path + '/'

def _error_message(resp):
    return "\nresponse is {0}\n".format(resp.text)

def generate_random_numeric_string(length):
    return ''.join(random.choices(string.digits, k=length))

def generate_random_alpha_string(length):
    return ''.join(random.choices(string.ascii_letters, k=length))

def generate_random_alphanumeric_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


class BaseAPI:

    @property
    def api_name(self):
        raise NotImplementedError

    def _endpoint_url(self, end_point):
        return _url(self.api_name) + '{0}/'.format(end_point)

    def _api_url(self):
        return _url(self.api_name)


class TestAuthAPI(BaseAPI):
  
    api_name = 'auth'
    valid_username = 'admin'
    valid_password = 'password'

    def login(self):
        return self._login(self.valid_username, self.valid_password)

    def logout(self, token):
        return requests.post(self._endpoint_url('logout'), json={'token':token})

    def validate(self, token):
        return requests.post(self._endpoint_url('validate'), json={'token':token})

    def _login(self, username, password):
        return requests.post(self._endpoint_url('login'), json={'password':password, 'username':username})

    def test_valid_login(self):
        resp = self.login()
        assert resp.status_code == 200, _error_message(resp)
        assert resp.json()['token']
        assert len(resp.json()['token']) == 16

    def test_invalid_login(self):
        resp = self._login('admin', 'welcome')
        assert resp.status_code == 403, _error_message(resp)

    def test_logout(self):
        token = self.login().json()['token']
        resp = self.logout(token)
        assert resp.status_code == 200, _error_message(resp)

    def test_valid_validate(self):
        token = self.login().json()['token']
        resp = self.validate(token)
        assert resp.status_code == 200, _error_message(resp)

    def test_invalid_validate(self):
        token = self.login().json()['token']
        invalid_token = token
        while invalid_token == token:
            invalid_token = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        resp = self.validate(invalid_token)
        assert resp.status_code == 403, _error_message(resp)

#test data for valid and invalid branding
update_branding_params = [dict(name_length=3, latitude=0, longitude=0, description_length=3, contact_name_length=3, address_length=10), 
                          dict(name_length=100, latitude=90, longitude=180, description_length=500, contact_name_length=40, address_length=200)]

@pytest.fixture(params=update_branding_params)
def update_branding_param(request):
    return request.param

invalid_update_branding_params = [dict(name_length=2), 
                                  dict(description_length=2),
                                  dict(contact_name_length=2),
                                  dict(address_length=9),
                                  dict(name_length=101),
                                  dict(description_length=501),
                                  dict(contact_name_length=41),
                                  dict(address_length=201)]

@pytest.fixture(params=invalid_update_branding_params)
def invalid_update_branding_param(request):
    return request.param


class TestBrandingAPI(BaseAPI):

    api_name = 'branding'
    default_branding = {
        "name": "Sauce Labs Retreat",
        "map": {
            "latitude": 37.7871917,
            "longitude": -122.4005403
         },
         "logoUrl": "https://automationintesting.com/images/supporters/saucelabs/020101_LOGO_Sauce-Labs_Vert_Red-Grey_RGB.png",
         "description": "Welcome to the Sauce Labs Retreat, the perfect space for continuous testing. Founded in 2008 and set in the glorious cross browser foothills of Foxfire and Pareo in the beautiful cloud, here you can take part in a wide range of activities including acting lessons for devices, painting for visual comparison and language lessons for Selenium, Appium, Espresso and more. So join us for your continuous testing solutions, stay for the hot sauce.",
         "contact": {
             "name": "Sauce Labs - USA (HQ)",
             "address": "116 New Montgomery St, 3rd Floor San Francisco, CA 94105 USA",
             "phone": "012345678901",
             "email": "https://saucelabs.com/sales"
         }
    }

    def get_branding(self):
        return requests.get(self._api_url())

    def update_branding(self, **kwargs):
        branding_json = self._generate_new_branding(**kwargs)
        token = TestAuthAPI().login().json()['token']
        return requests.put(self._api_url(), json=branding_json, cookies={'token':token})

    def _generate_new_branding(self, name_length=10, latitude=45, longitude=90, description_length=10, contact_name_length=10, address_length=20, phone_length=11, email_length=1):
        new_branding = self.default_branding
        new_branding['name'] = generate_random_alpha_string(name_length)
        new_branding['map']['latitude'] = latitude
        new_branding['map']['longitude'] = longitude
        new_branding['logoUrl'] = 'https://commons.wikimedia.org/wiki/File:Python-logo-notext.svg'
        new_branding['description'] = generate_random_alpha_string(description_length)
        new_branding['contact']['name'] = generate_random_alpha_string(contact_name_length)
        new_branding['contact']['address'] = generate_random_alphanumeric_string(address_length)
        new_branding['contact']['phone'] = generate_random_numeric_string(phone_length)
        new_branding['contact']['email'] = generate_random_alphanumeric_string(email_length)
        return new_branding

    def test_get_branding(self):
        resp = self.get_branding()
        assert resp.status_code == 200, _error_message(resp)

    def test_update_branding(self, update_branding_param):
        resp = self.update_branding(**update_branding_param)
        assert resp.status_code == 200, _error_message(resp)

    def test_invalid_update_branding(self, invalid_update_branding_param):
        resp = self.update_branding(**invalid_update_branding_param)
        assert resp.status_code == 400, _error_message(resp)

    def test_invalid_token_update_branding(self):
        branding_json = self._generate_new_branding(**update_branding_params[0])
        invalid_token = ''
        resp = requests.put(self._api_url(), json=branding_json, cookies={'token':invalid_token})
        assert resp.status_code == 403, _error_message(resp)

    #sql security vulnerability, api should limit length input and return a 400 error
    def test_sql_phone_length(self):
        resp = self.update_branding(phone_length=16)
        assert resp.status_code == 400, _error_message(resp)


class TestReportAPI(BaseAPI):

    api_name = 'report'

    def get_all_rooms_report(self):
        return requests.get(self._api_url())

    def get_room_report(self, room_id):
        return requests.get(self._endpoint_url('room') + '{0}/'.format(room_id))

    def test_get_all_rooms_report(self):
        resp = self.get_all_rooms_report()
        assert resp.status_code == 200, _error_message(resp)

    def test_get_room_report(self):
        resp = self.get_room_report(1)
        assert resp.status_code == 200, _error_message(resp)

#test data for valid and invalid messages
create_message_params = [dict(description_length=20, email_local_part_length=64, phone_length=11, subject_length=5), 
                          dict(description_length=2000, email_local_part_length=64, phone_length=21, subject_length=100)]

@pytest.fixture(params=create_message_params)
def create_message_param(request):
    return request.param

invalid_create_message_params = [dict(description_length=19), 
                                  dict(description_length=2001),
                                  dict(email_local_part_length=65),
                                  dict(email_local_part_length=0),
                                  dict(name_length=0),
                                  dict(phone_length=10),
                                  dict(phone_length=22),
                                  dict(subject_length=4),
                                  dict(subject_length=101)]

@pytest.fixture(params=invalid_create_message_params)
def invalid_create_message_param(request):
    return request.param


class TestMessageAPI(BaseAPI):

    api_name = 'message'

    def get_messages(self):
        return requests.get(self._api_url())

    def create_message(self, **kwargs):
        message_json = self._generate_new_message(**kwargs)
        return requests.post(self._api_url(), json=message_json)

    def get_message(self, message_id):
        return requests.get(self._endpoint_url(message_id))

    def delete_message(self, message_id, token):
        return requests.delete(self._endpoint_url(message_id) + 'delete/', cookies={'token':token})

    def read_message(self, message_id, token):
        return requests.put(self._endpoint_url(message_id) + 'read/', cookies={'token':token})

    def get_count(self):
        return requests.get(self._endpoint_url('count'))

    def _generate_new_message(self, description_length=100, email_local_part_length=10, email_domain_length=5, message_id=2, name_length=10, phone_length=11, subject_length=10):
        new_message = {
            "description": generate_random_alphanumeric_string(description_length),
            "email": generate_random_alphanumeric_string(email_local_part_length) + "@" + generate_random_alpha_string(email_domain_length) + ".com",
            "messageid": message_id,
            "name": generate_random_alpha_string(name_length),
            "phone": generate_random_numeric_string(phone_length),
            "subject": generate_random_alpha_string(subject_length)
        }
        return new_message

    def test_get_messages(self):
        resp = self.get_messages()
        assert resp.status_code == 200, _error_message(resp)

    def test_create_messages(self, create_message_param):
        resp = self.create_message(**create_message_param)
        assert resp.status_code == 200, _error_message(resp)

    def test_invalid_create_messages(self, invalid_create_message_param):
        resp = self.create_message(**invalid_create_message_param)
        assert resp.status_code == 400, _error_message(resp)

    def test_get_message(self):
        resp = self.get_message(1)
        assert resp.status_code == 200, _error_message(resp)

    def test_read_message(self):
        token = TestAuthAPI().login().json()['token']
        resp = self.read_message(1, token)
        assert resp.status_code == 200, _error_message(resp)

    def test_get_count(self):
        resp = self.get_count()
        assert resp.status_code == 200, _error_message(resp)


class TestRoomAPI(BaseAPI):

    api_name = 'room'

    def get_rooms(self):
        return requests.get(self._api_url())

    def create_room(self, **kwargs):
        token = TestAuthAPI().login().json()['token']
        room_json = self._generate_new_room(**kwargs)
        return requests.post(self._api_url(), json=room_json, cookies={'token':token})

    def get_room(self, room_id):
        return requests.get(self._endpoint_url(room_id))

    def update_room(self, room_id, room_json, token):
        return requests.put(self._endpoint_url(room_id), json=room_json, cookies={'token':token})

    def delete_room(self, room_id, token):
        return requests.delete(self._endpoint_url(room_id), cookies={'token':token})

    def _generate_new_room(self, accessible=True, description_length=100, features_length=10, room_number=random.randint(5, 100), room_price=random.randint(0, 999), room_type=random.choice(['Single', 'Double', 'Twin', 'Family', 'Suite'])):
        new_room = {
            "accessible": accessible,
            "description": generate_random_alpha_string(description_length),
            "features": [generate_random_alpha_string(features_length)],
            "image": 'https://commons.wikimedia.org/wiki/File:Python-logo-notext.svg',
            "roomNumber": room_number,
            "roomPrice": room_price,
            "roomid": 0,
            "type": room_type
        }
        return new_room

    def test_get_rooms(self):
        resp = self.get_rooms()
        assert resp.status_code == 200, _error_message(resp)

    def test_create_room(self):
        resp = self.create_room()
        assert resp.status_code == 200, _error_message(resp)


class TestBookingAPI(BaseAPI):

    api_name = 'booking'

    def get_bookings(self, room_id):
        return requests.get(self._api_url(), params={'roomid':room_id})

    def create_booking(self, checkin, checkout, roomid):
        token = TestAuthAPI().login().json()['token']
        booking_json = self._generate_new_booking(checkin, checkout, roomid)
        return requests.post(self._api_url(), json=booking_json, cookies={'token':token})

    def get_booking(self, room_id):
        return requests.get(self._endpoint_url(room_id))

    def update_booking(self, room_id, booking_json, token):
        return requests.put(self._endpoint_url(room_id), json=booking_json, cookies={'token':token})

    def delete_booking(self, room_id, token):
        return requests.delete(self._endpoint_url(room_id), cookies={'token':token})

    def _generate_new_booking(self, checkin, checkout, roomid, depositpaid=True, email_local_part_length=10, email_domain_length=5, firstname_length=5, lastname_length=5, phone_length=11):
        new_booking = {
            "bookingdates": {
                "checkin": checkin,
                "checkout": checkout},
            "bookingid": 0,
            "depositpaid": depositpaid,
            "email": generate_random_alphanumeric_string(email_local_part_length) + "@" + generate_random_alpha_string(email_domain_length) + ".com",
            "firstname": generate_random_alpha_string(firstname_length),
            "lastname": generate_random_alpha_string(lastname_length),
            "phone": generate_random_numeric_string(phone_length),
            "roomid": roomid
        }
        return new_booking

    def test_get_bookings(self):
        resp = self.get_bookings('1')
        assert resp.status_code == 200, _error_message(resp)

    def test_create_booking(self):
        resp = self.create_booking('2019-10-18T04:10:33.402Z', '2019-10-20T04:10:33.402Z', 1)
        assert resp.status_code == 200, _error_message(resp)