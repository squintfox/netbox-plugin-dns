from ipam.choices import IPAddressStatusChoices
from utilities.permissions import resolve_permission

from netbox_dns.models import Record, RecordTypeChoices, RecordStatusChoices


class DNSPermissionDenied(Exception):
    pass


def ipaddress_cf_data(ip_address):
    name = ip_address.custom_field_data.get("ipaddress_dns_record_name")
    ttl = ip_address.custom_field_data.get("ipaddress_dns_record_ttl")
    zone_id = ip_address.custom_field_data.get("ipaddress_dns_zone_id")

    if name is None or zone_id is None:
        return None, None, None

    return name, ttl, zone_id


def address_record_type(ip_address):
    return RecordTypeChoices.AAAA if ip_address.family == 6 else RecordTypeChoices.A


def address_record_status(ip_address):
    return (
        RecordStatusChoices.STATUS_ACTIVE
        if ip_address.status == IPAddressStatusChoices.STATUS_ACTIVE
        else RecordStatusChoices.STATUS_INACTIVE
    )


def get_address_record(ip_address):
    return ip_address.netbox_dns_records.first()


def new_address_record(instance):
    name, ttl, zone_id = ipaddress_cf_data(instance)

    if zone_id is None:
        return None

    return Record(
        name=name,
        zone_id=zone_id,
        ttl=ttl,
        status=address_record_status(instance),
        type=address_record_type(instance),
        value=str(instance.address.ip),
        ipam_ip_address_id=instance.id,
        managed=True,
    )


def update_address_record(record, ip_address):
    name, ttl, zone_id = ipaddress_cf_data(ip_address)

    record.name = name
    record.ttl = ttl
    record.zone_id = zone_id
    record.status = address_record_status(ip_address)
    record.value = str(ip_address.address.ip)


def check_permission(request, permission, record=None):
    if record is not None and record.pk is None:
        check_record = None
    else:
        check_record = record

    user = request.user

    if not user.has_perm(permission, check_record):
        action = resolve_permission(permission)[1]
        item = "records" if check_record is None else f"record {check_record}"

        raise DNSPermissionDenied(f"User {user} is not allowed to {action} DNS {item}")


def dns_changed(old, new):
    return any(
        (
            old.address.ip != new.address.ip,
            old.custom_field_data.get("ipaddress_dns_record_name")
            != new.custom_field_data.get("ipaddress_dns_record_name"),
            old.custom_field_data.get("ipaddress_dns_record_ttl")
            != new.custom_field_data.get("ipaddress_dns_record_ttl"),
            old.custom_field_data.get("ipaddress_dns_zone_id")
            != new.custom_field_data.get("ipaddress_dns_zone_id"),
        )
    )
