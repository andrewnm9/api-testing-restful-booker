import test_api_integration as api
import pytest
import json

def test_booking():
    """As a customer, I want to create a new booking and check that my booking is scheduled"""
    report_json = api.TestReportAPI().get_all_rooms_report().json()
    bookings_json = api.TestBookingAPI().get_bookings(1).json()
    api.TestBookingAPI().create_booking('2019-12-15T04:10:33.402Z', '2019-12-18T04:10:33.402Z', 1)
    new_report_json = api.TestReportAPI().get_all_rooms_report().json()
    new_bookings_json = api.TestBookingAPI().get_bookings(1).json()
    assert report_json != new_report_json
    assert bookings_json != new_bookings_json

def test_room():
    """As an admin, I want to create a new room and check that the new room is available"""
    rooms_json = api.TestRoomAPI().get_rooms().json()
    api.TestRoomAPI().create_room()
    new_rooms_json = api.TestRoomAPI().get_rooms().json()
    assert rooms_json != new_rooms_json

def test_message():
    """As a user I want to submit a new message, as an admin I want to view the new message"""
    messages_json = api.TestMessageAPI().get_messages().json()
    api.TestMessageAPI().create_message()
    new_messages_json = api.TestMessageAPI().get_messages().json()
    assert messages_json != new_messages_json
