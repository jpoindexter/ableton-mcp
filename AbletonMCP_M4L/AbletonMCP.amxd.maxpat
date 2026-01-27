{
    "patcher": {
        "fileversion": 1,
        "appversion": {
            "major": 8,
            "minor": 5,
            "revision": 0,
            "architecture": "x64",
            "modernui": 1
        },
        "classnamespace": "box",
        "rect": [100, 100, 400, 500],
        "bglocked": 0,
        "openinpresentation": 1,
        "default_fontsize": 12.0,
        "default_fontface": 0,
        "default_fontname": "Arial",
        "gridonopen": 1,
        "gridsize": [15.0, 15.0],
        "gridsnaponopen": 1,
        "objectsnaponopen": 1,
        "statusbarvisible": 2,
        "toolbarvisible": 1,
        "lefttoolbarpinned": 0,
        "toptoolbarpinned": 0,
        "righttoolbarpinned": 0,
        "bottomtoolbarpinned": 0,
        "toolbars_unpinned_last_save": 0,
        "tallnewobj": 0,
        "boxanimatetime": 200,
        "enablehscroll": 1,
        "enablevscroll": 1,
        "devicewidth": 0.0,
        "description": "AbletonMCP - Multi-Provider AI Music Assistant",
        "digest": "",
        "tags": "",
        "style": "",
        "subpatcher_template": "",
        "assistshowspatchername": 0,
        "boxes": [
            {
                "box": {
                    "id": "obj-title",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [15.0, 10.0, 200.0, 20.0],
                    "presentation": 1,
                    "presentation_rect": [10.0, 5.0, 180.0, 20.0],
                    "text": "AbletonMCP AI Assistant",
                    "fontface": 1,
                    "fontsize": 14.0
                }
            },
            {
                "box": {
                    "id": "obj-provider-label",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [15.0, 40.0, 60.0, 20.0],
                    "presentation": 1,
                    "presentation_rect": [10.0, 30.0, 60.0, 20.0],
                    "text": "Provider:"
                }
            },
            {
                "box": {
                    "id": "obj-provider-menu",
                    "maxclass": "umenu",
                    "numinlets": 1,
                    "numoutlets": 3,
                    "outlettype": ["int", "", ""],
                    "parameter_enable": 1,
                    "patching_rect": [80.0, 40.0, 120.0, 22.0],
                    "presentation": 1,
                    "presentation_rect": [70.0, 30.0, 120.0, 22.0],
                    "items": ["ollama", "openai", "claude", "groq"],
                    "saved_attribute_attributes": {
                        "valueof": {
                            "parameter_longname": "Provider",
                            "parameter_shortname": "Provider",
                            "parameter_type": 3,
                            "parameter_initial_enable": 1,
                            "parameter_initial": [0]
                        }
                    }
                }
            },
            {
                "box": {
                    "id": "obj-model-label",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [15.0, 70.0, 60.0, 20.0],
                    "presentation": 1,
                    "presentation_rect": [10.0, 55.0, 60.0, 20.0],
                    "text": "Model:"
                }
            },
            {
                "box": {
                    "id": "obj-model-input",
                    "maxclass": "textedit",
                    "numinlets": 1,
                    "numoutlets": 4,
                    "outlettype": ["", "int", "", ""],
                    "parameter_enable": 1,
                    "patching_rect": [80.0, 70.0, 120.0, 22.0],
                    "presentation": 1,
                    "presentation_rect": [70.0, 55.0, 120.0, 22.0],
                    "text": "llama3.2",
                    "saved_attribute_attributes": {
                        "valueof": {
                            "parameter_longname": "Model",
                            "parameter_shortname": "Model",
                            "parameter_type": 3
                        }
                    }
                }
            },
            {
                "box": {
                    "id": "obj-apikey-label",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [15.0, 100.0, 60.0, 20.0],
                    "presentation": 1,
                    "presentation_rect": [10.0, 80.0, 60.0, 20.0],
                    "text": "API Key:"
                }
            },
            {
                "box": {
                    "id": "obj-apikey-input",
                    "maxclass": "textedit",
                    "numinlets": 1,
                    "numoutlets": 4,
                    "outlettype": ["", "int", "", ""],
                    "parameter_enable": 1,
                    "patching_rect": [80.0, 100.0, 200.0, 22.0],
                    "presentation": 1,
                    "presentation_rect": [70.0, 80.0, 200.0, 22.0],
                    "text": "(not needed for Ollama)",
                    "saved_attribute_attributes": {
                        "valueof": {
                            "parameter_longname": "API Key",
                            "parameter_shortname": "API Key",
                            "parameter_type": 3
                        }
                    }
                }
            },
            {
                "box": {
                    "id": "obj-prompt-label",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [15.0, 140.0, 60.0, 20.0],
                    "presentation": 1,
                    "presentation_rect": [10.0, 110.0, 280.0, 20.0],
                    "text": "What would you like to create?"
                }
            },
            {
                "box": {
                    "id": "obj-prompt-input",
                    "maxclass": "textedit",
                    "numinlets": 1,
                    "numoutlets": 4,
                    "outlettype": ["", "int", "", ""],
                    "parameter_enable": 1,
                    "patching_rect": [15.0, 165.0, 350.0, 80.0],
                    "presentation": 1,
                    "presentation_rect": [10.0, 130.0, 280.0, 80.0],
                    "text": "Create a simple house beat at 124 BPM",
                    "lines": 4,
                    "saved_attribute_attributes": {
                        "valueof": {
                            "parameter_longname": "Prompt",
                            "parameter_shortname": "Prompt",
                            "parameter_type": 3
                        }
                    }
                }
            },
            {
                "box": {
                    "id": "obj-send-button",
                    "maxclass": "textbutton",
                    "numinlets": 1,
                    "numoutlets": 3,
                    "outlettype": ["", "", "int"],
                    "parameter_enable": 1,
                    "patching_rect": [15.0, 260.0, 100.0, 30.0],
                    "presentation": 1,
                    "presentation_rect": [10.0, 220.0, 100.0, 30.0],
                    "text": "Send",
                    "fontface": 1,
                    "saved_attribute_attributes": {
                        "valueof": {
                            "parameter_longname": "Send",
                            "parameter_shortname": "Send",
                            "parameter_type": 3
                        }
                    }
                }
            },
            {
                "box": {
                    "id": "obj-clear-button",
                    "maxclass": "textbutton",
                    "numinlets": 1,
                    "numoutlets": 3,
                    "outlettype": ["", "", "int"],
                    "parameter_enable": 1,
                    "patching_rect": [130.0, 260.0, 100.0, 30.0],
                    "presentation": 1,
                    "presentation_rect": [120.0, 220.0, 80.0, 30.0],
                    "text": "Clear",
                    "saved_attribute_attributes": {
                        "valueof": {
                            "parameter_longname": "Clear",
                            "parameter_shortname": "Clear",
                            "parameter_type": 3
                        }
                    }
                }
            },
            {
                "box": {
                    "id": "obj-status",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [220.0, 265.0, 150.0, 20.0],
                    "presentation": 1,
                    "presentation_rect": [210.0, 225.0, 80.0, 20.0],
                    "text": "Ready",
                    "textcolor": [0.2, 0.7, 0.3, 1.0]
                }
            },
            {
                "box": {
                    "id": "obj-response-label",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [15.0, 300.0, 60.0, 20.0],
                    "presentation": 1,
                    "presentation_rect": [10.0, 255.0, 280.0, 20.0],
                    "text": "Response:"
                }
            },
            {
                "box": {
                    "id": "obj-response-output",
                    "maxclass": "textedit",
                    "numinlets": 1,
                    "numoutlets": 4,
                    "outlettype": ["", "int", "", ""],
                    "patching_rect": [15.0, 325.0, 350.0, 120.0],
                    "presentation": 1,
                    "presentation_rect": [10.0, 275.0, 280.0, 120.0],
                    "readonly": 1,
                    "text": "AI responses will appear here...",
                    "lines": 6
                }
            },
            {
                "box": {
                    "id": "obj-node-script",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": ["", ""],
                    "patching_rect": [15.0, 480.0, 150.0, 22.0],
                    "text": "node.script code/main.js"
                }
            },
            {
                "box": {
                    "id": "obj-route-response",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 3,
                    "outlettype": ["", "", ""],
                    "patching_rect": [15.0, 510.0, 150.0, 22.0],
                    "text": "route response status"
                }
            },
            {
                "box": {
                    "id": "obj-prepend-chat",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [""],
                    "patching_rect": [15.0, 450.0, 80.0, 22.0],
                    "text": "prepend chat"
                }
            },
            {
                "box": {
                    "id": "obj-prepend-provider",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [""],
                    "patching_rect": [200.0, 70.0, 100.0, 22.0],
                    "text": "prepend setProvider"
                }
            },
            {
                "box": {
                    "id": "obj-prepend-model",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [""],
                    "patching_rect": [200.0, 100.0, 100.0, 22.0],
                    "text": "prepend setModel"
                }
            },
            {
                "box": {
                    "id": "obj-prepend-apikey",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [""],
                    "patching_rect": [280.0, 130.0, 100.0, 22.0],
                    "text": "prepend setApiKey"
                }
            },
            {
                "box": {
                    "id": "obj-clear-msg",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [""],
                    "patching_rect": [130.0, 300.0, 80.0, 22.0],
                    "text": "clearHistory"
                }
            },
            {
                "box": {
                    "id": "obj-live-api",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [""],
                    "patching_rect": [250.0, 480.0, 80.0, 22.0],
                    "text": "live.thisdevice"
                }
            }
        ],
        "lines": [
            {
                "patchline": {
                    "source": ["obj-prompt-input", 0],
                    "destination": ["obj-prepend-chat", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-prepend-chat", 0],
                    "destination": ["obj-node-script", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-node-script", 0],
                    "destination": ["obj-route-response", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-route-response", 0],
                    "destination": ["obj-response-output", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-route-response", 1],
                    "destination": ["obj-status", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-provider-menu", 1],
                    "destination": ["obj-prepend-provider", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-prepend-provider", 0],
                    "destination": ["obj-node-script", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-model-input", 0],
                    "destination": ["obj-prepend-model", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-prepend-model", 0],
                    "destination": ["obj-node-script", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-apikey-input", 0],
                    "destination": ["obj-prepend-apikey", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-prepend-apikey", 0],
                    "destination": ["obj-node-script", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-send-button", 0],
                    "destination": ["obj-prompt-input", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-clear-button", 0],
                    "destination": ["obj-clear-msg", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-clear-msg", 0],
                    "destination": ["obj-node-script", 0]
                }
            }
        ],
        "parameters": {
            "obj-provider-menu": {
                "parameter_initial": [0],
                "parameter_initial_enable": 1
            }
        },
        "dependency_cache": [],
        "autosave": 0
    }
}
