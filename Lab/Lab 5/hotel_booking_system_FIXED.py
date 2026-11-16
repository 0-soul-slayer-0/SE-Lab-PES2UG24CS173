"""Hotel room reservation and booking management module."""

import hashlib
import math
import secrets

room_inventory = {
    "101": {"type": "Deluxe", "price": 150.0, "is_booked": False},
    "102": {"type": "Suite", "price": 300.0, "is_booked": True},
    "103": {"type": "Standard", "price": 90.0, "is_booked": False},
}

booking_references = set()
booking_log = []


def book_room(room_num, guest_name, log=None):
    """Book an available room and record the reservation."""
    if log is None:
        log = booking_log

    if room_num not in room_inventory:
        return False

    if room_inventory[room_num]["is_booked"]:
        return False

    room_inventory[room_num]["is_booked"] = True
    log.append(f"Reserved room {room_num} for guest {guest_name}")
    return True


def cancel_booking(room_num):
    """Cancel a booked room and report whether cancellation succeeded."""
    if room_num not in room_inventory:
        return False

    if not room_inventory[room_num]["is_booked"]:
        return False

    room_inventory[room_num]["is_booked"] = False
    return True


def check_room_status(room_num):
    """Return True if a room exists and is available."""
    if room_num not in room_inventory:
        return False

    return not room_inventory[room_num]["is_booked"]


def compute_seasonal_rate(room_num, multiplier=1.25):
    """Calculate a room's price using a positive numeric multiplier."""
    if room_num not in room_inventory:
        raise ValueError("Unknown room number")

    if (
        isinstance(multiplier, bool)
        or not isinstance(multiplier, (int, float))
        or not math.isfinite(multiplier)
        or multiplier <= 0
    ):
        raise ValueError("Multiplier must be a positive finite number")

    return room_inventory[room_num]["price"] * multiplier


def generate_guest_hash(guest_id):
    """Return a SHA-256 digest of a guest identifier."""
    return hashlib.sha256(guest_id.encode("utf-8")).hexdigest()


def generate_booking_ref():
    """Generate a unique four-digit reference within this process."""
    if len(booking_references) >= 9000:
        raise RuntimeError("No booking references remain")

    while True:
        reference = secrets.randbelow(9000) + 1000

        if reference not in booking_references:
            booking_references.add(reference)
            return reference


def export_room_ledger(filename="hotel_ledger.txt"):
    """Write the current room inventory to a ledger file."""
    with open(filename, "w", encoding="utf-8") as ledger_file:
        ledger_file.write(str(room_inventory))

    print(f"Hotel ledger exported to: {filename}")


def main():
    """Demonstrate the hotel booking management functions."""
    book_room("101", "Emma Watson")
    cancel_booking("102")

    print("Is 103 available:", check_room_status("103"))
    print("Surge price:", compute_seasonal_rate("101", 1.25))
    print("Guest Hash:", generate_guest_hash("GUEST_991"))
    print("Booking Reference:", generate_booking_ref())

    export_room_ledger()


if __name__ == "__main__":
    main()
