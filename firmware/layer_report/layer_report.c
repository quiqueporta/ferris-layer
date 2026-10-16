#include "layer_report.h"
#include "raw_hid.h"

#define LAYER_REPORT_SIZE 32

static void send_layer(uint8_t layer) {
    uint8_t report[LAYER_REPORT_SIZE] = {'L', 'Y', layer};

    raw_hid_send(report, sizeof(report));
}

void layer_report_announce(layer_state_t state) {
    send_layer(get_highest_layer(state));
}

bool layer_report_answer(uint8_t *data) {
    bool asks_current_layer = data[0] == 'L' && data[1] == 'Y';
    if (asks_current_layer) {
        send_layer(get_highest_layer(layer_state));
    }

    return asks_current_layer;
}
