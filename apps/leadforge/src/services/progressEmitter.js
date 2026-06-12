const { EventEmitter } = require('events');

// Singleton event bus — scrapers emit here, SSE routes listen here
const emitter = new EventEmitter();
emitter.setMaxListeners(50);

module.exports = emitter;
