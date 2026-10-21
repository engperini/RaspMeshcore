#include "../include/RadioTransport.h"
#include <cassert>
#include <cstdint>
#include <stdexcept>
#include <vector>
using namespace raspmeshcore;
struct Fake : RadioTransport {
  bool busy = false;
  bool opened = false;
  std::vector<uint8_t> captured;
  void open() override { opened = true; }
  void close() noexcept override { opened = false; }
  void transfer(const uint8_t* tx, uint8_t* rx, std::size_t n) override {
    if (!opened) throw std::runtime_error("closed");
    captured.assign(tx, tx + n);
    for (std::size_t i=0; i<n; ++i) rx[i] = tx[i];
  }
  void write(RadioSignal, bool) override {}
  bool read(RadioSignal s) override { return s == RadioSignal::Busy && busy; }
};
int main() {
  Fake fake;
  fake.open();
  std::vector<uint8_t> tx(255, 0xAB), rx(255);
  tx[0] = 0x0E; tx[1] = 0;
  fake.transfer(tx.data(), rx.data(), tx.size());
  assert(fake.captured == tx && rx == tx);
  waitBusyLow(fake);
  fake.busy = true;
  bool timeout = false;
  try { waitBusyLow(fake, 2); } catch (const std::runtime_error&) { timeout = true; }
  assert(timeout);
  fake.close();
  return 0;
}
