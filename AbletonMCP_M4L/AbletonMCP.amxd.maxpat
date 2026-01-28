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
		"rect": [100, 100, 600, 600],
		"openrect": [0.0, 0.0, 300.0, 450.0],
		"bglocked": 0,
		"openinpresentation": 1,
		"default_fontsize": 10.0,
		"default_fontface": 0,
		"default_fontname": "Arial",
		"gridonopen": 1,
		"gridsize": [8.0, 8.0],
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
		"devicewidth": 300.0,
		"description": "AbletonMCP - AI Music Assistant",
		"digest": "",
		"tags": "",
		"style": "",
		"subpatcher_template": "",
		"boxes": [
			{
				"box": {
					"id": "obj-title",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [15.0, 10.0, 200.0, 18.0],
					"presentation": 1,
					"presentation_rect": [5.0, 2.0, 150.0, 18.0],
					"text": "AbletonMCP",
					"fontface": 1,
					"fontsize": 11.0
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
					"patching_rect": [15.0, 35.0, 90.0, 20.0],
					"presentation": 1,
					"presentation_rect": [5.0, 22.0, 70.0, 18.0],
					"fontsize": 10.0,
					"items": ["ollama", ",", "openai", ",", "claude", ",", "groq"],
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
					"id": "obj-model-input",
					"maxclass": "textedit",
					"numinlets": 1,
					"numoutlets": 4,
					"outlettype": ["", "int", "", ""],
					"parameter_enable": 1,
					"patching_rect": [120.0, 35.0, 100.0, 20.0],
					"presentation": 1,
					"presentation_rect": [78.0, 22.0, 80.0, 18.0],
					"fontsize": 10.0,
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
					"id": "obj-apikey-input",
					"maxclass": "textedit",
					"numinlets": 1,
					"numoutlets": 4,
					"outlettype": ["", "int", "", ""],
					"parameter_enable": 1,
					"patching_rect": [240.0, 35.0, 150.0, 20.0],
					"presentation": 1,
					"presentation_rect": [161.0, 22.0, 130.0, 18.0],
					"fontsize": 9.0,
					"text": "",
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
					"id": "obj-prompt-input",
					"maxclass": "textedit",
					"numinlets": 1,
					"numoutlets": 4,
					"outlettype": ["", "int", "", ""],
					"parameter_enable": 1,
					"patching_rect": [15.0, 65.0, 280.0, 40.0],
					"presentation": 1,
					"presentation_rect": [5.0, 42.0, 250.0, 40.0],
					"fontsize": 10.0,
					"text": "",
					"lines": 2,
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
					"patching_rect": [15.0, 115.0, 50.0, 20.0],
					"presentation": 1,
					"presentation_rect": [258.0, 42.0, 35.0, 18.0],
					"text": "Send",
					"fontsize": 10.0,
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
					"patching_rect": [75.0, 115.0, 50.0, 20.0],
					"presentation": 1,
					"presentation_rect": [258.0, 63.0, 35.0, 18.0],
					"text": "Clr",
					"fontsize": 10.0,
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
					"patching_rect": [140.0, 115.0, 100.0, 18.0],
					"presentation": 1,
					"presentation_rect": [5.0, 84.0, 80.0, 18.0],
					"text": "Ready",
					"fontsize": 10.0,
					"textcolor": [0.2, 0.7, 0.3, 1.0]
				}
			},
			{
				"box": {
					"id": "obj-response-output",
					"maxclass": "textedit",
					"numinlets": 1,
					"numoutlets": 4,
					"outlettype": ["", "int", "", ""],
					"patching_rect": [15.0, 145.0, 280.0, 80.0],
					"presentation": 1,
					"presentation_rect": [5.0, 100.0, 288.0, 65.0],
					"readonly": 1,
					"fontsize": 9.0,
					"text": "",
					"lines": 4
				}
			},
			{
				"box": {
					"id": "obj-node-script",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": ["", ""],
					"patching_rect": [15.0, 280.0, 150.0, 20.0],
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
					"patching_rect": [15.0, 310.0, 150.0, 20.0],
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
					"patching_rect": [15.0, 250.0, 80.0, 20.0],
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
					"patching_rect": [200.0, 250.0, 110.0, 20.0],
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
					"patching_rect": [340.0, 250.0, 100.0, 20.0],
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
					"patching_rect": [460.0, 250.0, 100.0, 20.0],
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
					"patching_rect": [75.0, 140.0, 80.0, 20.0],
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
					"patching_rect": [300.0, 280.0, 90.0, 20.0],
					"text": "live.thisdevice"
				}
			},
			{
				"box": {
					"id": "obj-plugin-in",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": ["signal", "signal"],
					"patching_rect": [300.0, 350.0, 55.0, 20.0],
					"text": "plugin~"
				}
			},
			{
				"box": {
					"id": "obj-plugin-out",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 0,
					"patching_rect": [300.0, 380.0, 65.0, 20.0],
					"text": "plugout~"
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
			},
			{
				"patchline": {
					"source": ["obj-plugin-in", 0],
					"destination": ["obj-plugin-out", 0]
				}
			},
			{
				"patchline": {
					"source": ["obj-plugin-in", 1],
					"destination": ["obj-plugin-out", 1]
				}
			}
		],
		"dependency_cache": [],
		"latency": 0,
		"project": {
			"version": 1,
			"creationdate": 3590052493,
			"modificationdate": 3590052493,
			"viewrect": [0.0, 0.0, 300.0, 500.0],
			"autoorganize": 1,
			"hideprojectwindow": 1,
			"showdependencies": 1,
			"autolocalize": 0,
			"contents": {
				"patchers": {},
				"code": {}
			},
			"layout": {},
			"searchpath": {},
			"detailsvisible": 0,
			"amxdtype": 1633771873,
			"readonly": 0,
			"devpathtype": 0,
			"devpath": ".",
			"sortmode": 0,
			"viewmode": 0
		},
		"autosave": 0
	}
}
