import { describe, it, expect } from "vitest";
import { inferBrand, sha256 } from "../worker/index";

describe("inferBrand", () => {
  it("routes handy hearts to grissom", () => {
    expect(inferBrand("handy-hearts")).toBe("grissom");
  });
  it("routes cedar hollow to grissom", () => {
    expect(inferBrand("cedar-hollow-book-one")).toBe("grissom");
  });
  it("routes gothic titles to grissom", () => {
    expect(inferBrand("gothic-nights")).toBe("grissom");
  });
  it("routes spooky titles to grissom", () => {
    expect(inferBrand("spooky-coloring")).toBe("grissom");
  });
  it("routes familybook explicitly", () => {
    expect(inferBrand("familybook-01")).toBe("familybook");
  });
  it("routes kids to familybook", () => {
    expect(inferBrand("kids-coloring-01")).toBe("familybook");
  });
  it("routes ora explicitly", () => {
    expect(inferBrand("ora-launch")).toBe("ora");
  });
  it("defaults unknown to grissom (pilot)", () => {
    expect(inferBrand("random-unknown-sku")).toBe("grissom");
  });
  it("is case-insensitive", () => {
    expect(inferBrand("HANDY-HEARTS")).toBe("grissom");
  });
});

describe("sha256", () => {
  it("produces a hex string of length 64", async () => {
    const h = await sha256("hello");
    expect(h).toMatch(/^[0-9a-f]{64}$/);
  });
  it("is deterministic", async () => {
    const a = await sha256("same input");
    const b = await sha256("same input");
    expect(a).toBe(b);
  });
  it("differs for different inputs", async () => {
    const a = await sha256("input a");
    const b = await sha256("input b");
    expect(a).not.toBe(b);
  });
  it("differs when salt changes (documents rotation)", async () => {
    const a = await sha256("1.2.3.4" + "salt-day-1");
    const b = await sha256("1.2.3.4" + "salt-day-2");
    expect(a).not.toBe(b);
  });
});

describe("attribution contract", () => {
  it("post_id format is YYYY-MM-DD-HHMM", () => {
    const example = "2026-08-14-1400";
    expect(example).toMatch(/^\d{4}-\d{2}-\d{2}-\d{4}$/);
  });
});
