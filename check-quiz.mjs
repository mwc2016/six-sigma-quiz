// Run: node check-quiz.mjs. No browser or test dependencies.
import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";

const html = fs.readFileSync("index.html", "utf8");
assert.equal(html, fs.readFileSync("dist/index.html", "utf8"), "Published output must match source");
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];
new vm.Script(script);

const bankStart = script.indexOf("const bank =");
const setsStart = script.indexOf("    const sets =", bankStart);
assert.ok(bankStart >= 0 && setsStart > bankStart);
const bank = JSON.parse(vm.runInNewContext(script.slice(bankStart, setsStart) + "; JSON.stringify(bank);"));
const {sets} = bank;
const categories = [
  "Foundations and TOCLSS",
  "Define and Project Selection",
  "Process Analysis and Lean Transformation",
  "Measure and Data Collection",
  "MSA and FMEA",
  "Analyze and Root Cause",
  "Statistical Data Analysis",
  "Improve and DOE",
  "Control and SPC",
  "Project and SSI Certification",
];

assert.deepEqual(sets.map(set => set.questions.length), [150, 150]);
assert.deepEqual(sets.map(set => set.id), ["ssi-exam-practice", "ssi-applied-scenarios"]);
const questions = sets.flatMap(set => set.questions);
assert.equal(questions.length, 300);
assert.equal(new Set(questions.map(question => question.id)).size, 300);
const normalise = value => value.toLowerCase().replace(/[^a-z0-9]/g, "");
assert.equal(new Set(questions.map(question => normalise(question.q))).size, 300, "Question text must be unique");

sets.forEach((set, index) => {
  const counts = new Map(categories.map(category => [category, 0]));
  set.questions.forEach(question => {
    counts.set(question.category, (counts.get(question.category) || 0) + 1);
    assert.equal(question.o.length, 4);
    assert.equal(new Set(question.o).size, 4);
    assert.ok(question.q && question.e && question.topic && question.source);
    assert.ok(["concept", "scenario", "calculation"].includes(question.kind));
    assert.ok(Number.isInteger(question.a) && question.a >= 0 && question.a < 4);
    assert.ok(bank.sources[question.source]);
  });
  assert.deepEqual([...counts.keys()], categories);
  assert.ok([...counts.values()].every(count => count === 15));
  const scenarios = set.questions.filter(question => question.kind === "scenario").length;
  const calculations = set.questions.filter(question => question.kind === "calculation").length;
  assert.ok(scenarios >= (index === 0 ? 20 : 100));
  assert.ok(calculations <= 45);
});

const expectedAnswers = new Map([
  ["A-015", "4 minutes per case"],
  ["A-038", "4 hours"],
  ["A-039", "3 minutes per unit"],
  ["A-045", "20%"],
  ["A-052", "11 minutes"],
  ["A-053", "7 kg"],
  ["A-055", "0.03"],
  ["A-056", "10,000"],
  ["A-058", "0.855"],
  ["A-059", "8,000 PPM"],
  ["A-071", "96"],
  ["A-090", "80%"],
  ["A-105", "4 times as many observations"],
  ["A-107", "8"],
  ["A-119", "32"],
  ["A-143", "HK$120,000"],
  ["A-149", "98 hours"],
  ["B-014", "5 minutes per case"],
  ["B-015", "2 cases per hour"],
  ["B-036", "4 minutes per claim"],
  ["B-044", "10%"],
  ["B-050", "20,000 PPM"],
  ["B-051", "15,000"],
  ["B-052", "0.931"],
  ["B-073", "140"],
  ["B-074", "96"],
  ["B-090", "80%"],
  ["B-104", "4 times"],
  ["B-107", "16"],
  ["B-140", "HK$20,000"],
  ["B-147", "Below the stated passing mark"],
  ["B-149", "98 hours"],
]);
const byId = new Map(questions.map(question => [question.id, question]));
assert.equal(expectedAnswers.size, questions.filter(question => question.kind === "calculation").length, "Every calculation question must have a checked answer");
for (const [id, answer] of expectedAnswers) assert.equal(byId.get(id).o[byId.get(id).a], answer, id);

// Small DOM/event stand-in for answer entry, grading, tabs, persistence, and timer lifecycle.
class Element {
  constructor(tag = "div") {
    this.tagName = tag;
    this.children = [];
    this.attrs = {};
    this.listeners = {};
    this.dataset = {};
    this.className = "";
    this.textContent = "";
    this.hidden = true;
    this.value = 0;
    this._html = "";
    this.classList = {add() {}, remove() {}, toggle() {}};
  }
  set innerHTML(value) {
    this._html = value;
    this.children = [];
    if (this.tagName === "fieldset") {
      this.options = [...value.matchAll(/<input id="([^"]+)" type="radio" name="([^"]+)" value="(\d)"([^>]*)>/g)].map(match => {
        const input = new Element("input");
        input.id = match[1];
        input.name = match[2];
        input.type = "radio";
        input.value = match[3];
        input.checked = match[4].includes("checked");
        input.parent = this;
        const label = new Element("label");
        input.label = label;
        return input;
      });
      this.feedback = new Element("p");
    }
  }
  get innerHTML() { return this._html; }
  append(child) { this.children.push(child); }
  setAttribute(key, value) { this.attrs[key] = value; }
  addEventListener(type, handler) { (this.listeners[type] ??= []).push(handler); }
  emit(type, event = {}) { for (const handler of this.listeners[type] || []) handler(event); }
  focus() {}
  closest(selector) { return selector === "fieldset" ? this.parent : this.label; }
  querySelector(selector) {
    if (selector === "input:checked") return this.options.find(input => input.checked) || null;
    if (selector === ".feedback") return this.feedback;
    return null;
  }
  querySelectorAll(selector) { return selector === "label" ? this.options.map(input => input.label) : []; }
}

function app(saved = new Map(), badStorage = false) {
  let now = 0;
  let focused = true;
  const elements = new Map();
  const doc = new Element();
  const win = new Element();
  const element = id => {
    if (!elements.has(id)) elements.set(id, new Element());
    return elements.get(id);
  };
  doc.visibilityState = "visible";
  doc.hasFocus = () => focused;
  doc.createElement = tag => new Element(tag);
  doc.querySelector = selector => selector.startsWith("#question-")
    ? element("#quiz").children.find(child => child.id === selector.slice(1))
    : element(selector);
  win.scrollTo = () => {};
  let interval;
  const ctx = vm.createContext({
    document: doc,
    window: win,
    performance: {now: () => now},
    setInterval: handler => { interval = handler; },
    localStorage: {
      getItem: key => {
        if (badStorage) throw Error("disabled");
        return saved.get(key) ?? null;
      },
      setItem: (key, value) => {
        if (badStorage) throw Error("full");
        saved.set(key, value);
      },
      removeItem: key => saved.delete(key),
    },
    console,
  });
  vm.runInContext(script, ctx);
  return {
    saved,
    doc,
    win,
    element,
    eval: expression => vm.runInContext(expression, ctx),
    advance: milliseconds => { now += milliseconds; },
    tick: () => interval(),
    focus: state => { focused = state; win.emit(state ? "focus" : "blur"); },
  };
}

const progressA = "lean-six-sigma-progress-v3-ssi-exam-practice";
const progressB = "lean-six-sigma-progress-v3-ssi-applied-scenarios";
const timeA = "lean-six-sigma-time-v3-ssi-exam-practice";
const timeB = "lean-six-sigma-time-v3-ssi-applied-scenarios";
const saved = new Map([[progressA, JSON.stringify({answers: {"A-001": byId.get("A-001").a}, randomMode: false})]]);
const app1 = app(saved);
assert.equal(app1.element("#setTabs").children.length, 2);
assert.equal(app1.element("#quiz").children.filter(child => child.tagName === "fieldset").length, 150);
assert.equal(app1.eval('answers["A-001"]'), byId.get("A-001").a);
app1.advance(4200); app1.tick();
assert.equal(app1.element("#timer").textContent, "00:00:04");
app1.focus(false); app1.advance(9000); app1.tick();
assert.equal(app1.eval("currentElapsed()"), 4200, "Blur pauses the timer");
app1.focus(true); app1.advance(800); app1.doc.visibilityState = "hidden"; app1.doc.emit("visibilitychange");
app1.advance(100000); app1.tick();
assert.equal(app1.eval("currentElapsed()"), 5000, "Hidden time is excluded");
app1.doc.visibilityState = "visible"; app1.doc.emit("visibilitychange"); app1.advance(2000);
app1.eval("selectSet(1)");
assert.equal(app1.element("#quiz").children.filter(child => child.tagName === "fieldset").length, 150);
assert.equal(app1.eval("currentElapsed()"), 0);
app1.advance(3500); app1.tick();
const appliedId = sets[1].questions[0].id;
app1.eval(`answers[${JSON.stringify(appliedId)}] = 2; saveProgress();`);
app1.element("#randomButton").emit("click");
assert.equal(app1.eval("randomMode"), true);
assert.equal(app1.eval("new Set(questionOrder.map(question => question.id)).size"), 150);
app1.eval("selectSet(0)");
assert.equal(app1.eval("currentElapsed()"), 7000, "Set A time is restored");
app1.eval("selectSet(1)");
assert.equal(app1.eval("currentElapsed()"), 3500, "Set B time is restored");
assert.equal(app1.eval(`answers[${JSON.stringify(appliedId)}]`), 2);
assert.equal(app1.eval("randomMode"), true, "Random order is saved per set");
app1.element("#restartTimer").emit("click");
assert.equal(app1.eval("currentElapsed()"), 0);
assert.equal(app1.eval(`answers[${JSON.stringify(appliedId)}]`), 2, "Restart keeps answers");
app1.advance(2000); app1.win.emit("pagehide"); app1.advance(999999); app1.tick();
assert.equal(app1.eval("currentElapsed()"), 2000, "Closed-page time is excluded");

const app2 = app(saved);
assert.equal(app2.eval("activeSet"), 1);
assert.equal(app2.eval("currentElapsed()"), 2000, "Reload restores accrued time");
app2.element("#resetButton").emit("click");
assert.equal(app2.eval("Object.keys(answers).length"), 0);
assert.equal(app2.eval("currentElapsed()"), 2000, "Answer reset keeps time");
app2.eval("selectSet(0)");
assert.equal(app2.eval('answers["A-001"]'), byId.get("A-001").a, "Reset is isolated to the active set");
app2.element("#verifyButton").emit("click");
assert.match(app2.element("#scoreText").textContent, /1\/1 correct/);
app2.eval("selectSet(1)");
for (const position of [0, 1, 2, 3]) {
  const question = sets[1].questions.find(item => item.a === position);
  const field = app2.element("#quiz").children.find(child => child.id === `question-${question.id}`);
  const input = field.options[position];
  input.checked = true;
  app2.element("#quiz").emit("change", {target: input});
}
app2.element("#verifyButton").emit("click");
assert.match(app2.element("#scoreText").textContent, /4\/4 correct/);
app2.element("#setTabs").children[1].emit("keydown", {key: "Home", preventDefault() {}});
assert.equal(app2.eval("activeSet"), 0);
app2.element("#setTabs").children[0].emit("keydown", {key: "End", preventDefault() {}});
assert.equal(app2.eval("activeSet"), 1);
app2.doc.emit("freeze"); app2.advance(5000); app2.tick();
const stopped = app2.eval("currentElapsed()");
app2.doc.emit("resume"); app2.advance(1000);
assert.equal(app2.eval("currentElapsed()"), stopped + 1000);

const shared = new Map();
const first = app(shared);
first.advance(3000); first.focus(false);
const second = app(shared);
second.advance(2000); second.focus(false);
first.advance(5000); first.tick(); first.focus(true);
assert.equal(first.eval("currentElapsed()"), 5000, "Focus reloads time from another window");
assert.equal(app(new Map(), true).element("#storageWarning").hidden, false, "Storage failure is visible");
const corrupt = new Map([[timeA, "-100"], [timeB, "not-a-number"]]);
assert.equal(app(corrupt).eval("currentElapsed()"), 0, "Invalid saved time cannot produce a negative timer");
console.log("PASS: 300 SSI questions; two 150-question tabs; 10 categories × 15 per tab; practical-scenario balance; calculation keys; source/output match; answer, grading, shuffle, keyboard, timer, persistence, and storage checks.");
