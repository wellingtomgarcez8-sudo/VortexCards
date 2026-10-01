import asyncio
import pytest
from vortexcards.networking.protocol import make_message, encode_message, validate_message, PROTOCOL_VERSION

def test_protocol_message_shape():
    m=make_message("PING",{});assert m["protocol_version"]==PROTOCOL_VERSION;validate_message(m)

def test_invalid_type_rejected():
    with pytest.raises(ValueError):make_message("CHEAT",{})

def test_packet_is_length_prefixed():
    data=encode_message(make_message("PING",{}));assert len(data)>4
