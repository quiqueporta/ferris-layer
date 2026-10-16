#pragma once

#include "quantum.h"

// Sends "LY" + highest active layer over Raw HID. Call it from layer_state_set_user().
void layer_report_announce(layer_state_t state);

// Answers the host's "LY" request with the current layer. Return its result from via_command_kb().
bool layer_report_answer(uint8_t *data);
