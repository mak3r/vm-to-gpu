# vm_to_gpu/config_manager.py
import os
import json

CONFIG_DIR = os.path.expanduser("~/.config/vm-to-gpu")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

def ensure_config_dir_exists():
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)

def load_config():
    ensure_config_dir_exists()
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as file:
            return json.load(file)
    return {"domains": []}

def save_config(config):
    ensure_config_dir_exists()
    with open(CONFIG_FILE, 'w') as file:
        json.dump(config, file, indent=4)

def create_domain(name, system):
    config = load_config()
    new_domain = {
        "name": name,
        "system": system,
        "devices": []
    }
    config["domains"].append(new_domain)
    save_config(config)
    return new_domain

def update_domain(domain_index, name=None, system=None):
    config = load_config()
    if domain_index < len(config["domains"]):
        if name:
            config["domains"][domain_index]["name"] = name
        if system:
            config["domains"][domain_index]["system"] = system
        save_config(config)
        return config["domains"][domain_index]
    return None

def delete_domain(domain_index):
    config = load_config()
    if domain_index < len(config["domains"]):
        deleted_domain = config["domains"].pop(domain_index)
        save_config(config)
        return deleted_domain
    return None

def add_device_to_domain(domain_index, vendor, product, vendor0x, product0x, enabled):
    config = load_config()
    if domain_index < len(config["domains"]):
        new_device = {
            "vendor": vendor,
            "product": product,
            "vendor0x": vendor0x,
            "product0x": product0x,
            "enabled": enabled
        }
        config["domains"][domain_index]["devices"].append(new_device)
        save_config(config)
        return new_device
    return None

def update_device_in_domain(domain_index, device_index, vendor=None, product=None, vendor0x=None, product0x=None, enabled=None):
    config = load_config()
    if domain_index < len(config["domains"]) and device_index < len(config["domains"][domain_index]["devices"]):
        device = config["domains"][domain_index]["devices"][device_index]
        if vendor:
            device["vendor"] = vendor
        if product:
            device["product"] = product
        if vendor0x:
            device["vendor0x"] = vendor0x
        if product0x:
            device["product0x"] = product0x
        if enabled is not None:
            device["enabled"] = enabled
        save_config(config)
        return device
    return None

def delete_device_from_domain(domain_index, device_index):
    config = load_config()
    if domain_index < len(config["domains"]) and device_index < len(config["domains"][domain_index]["devices"]):
        deleted_device = config["domains"][domain_index]["devices"].pop(device_index)
        save_config(config)
        return deleted_device
    return None