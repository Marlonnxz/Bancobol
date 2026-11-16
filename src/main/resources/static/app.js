'use strict';

const $ = (s) => document.querySelector(s);
const cop = new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP' });
const fechaFmt = new Intl.DateTimeFormat('es-CO', { dateStyle: 'medium', timeStyle: 'short' });
const TEL = /^\d{10}$/;
const KEY = 'bancobol.telefono';

let cuenta = null;

const store = {
  get() { try { return localStorage.getItem(KEY); } catch { return null; } },
  set(v) { try { localStorage.setItem(KEY, v); } catch { /* sin storage */ } },
  del() { try { localStorage.removeItem(KEY); } catch { /* sin storage */ } },
};

async function api(path, body) {
  const opts = body === undefined ? {} : {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  };
  let res;
  try { res = await fetch(path, opts); } catch { throw new Error('No hay conexión con el servidor'); }
  const data = await res.json().catch(() => null);
  if (!res.ok) throw new Error((data && data.error) || `Error ${res.status}`);
  return data;
}

function msg(el, text, ok) {
  el.textContent = text || '';
  el.className = 'msg' + (text ? (ok ? ' ok' : ' err') : '');
}

function show(id) {
  document.querySelectorAll('.view').forEach((v) => { v.hidden = v.id !== id; });
  const view = document.getElementById(id);
  view.querySelectorAll('.msg').forEach((m) => msg(m, ''));
  if (id === 'v-inicio') refrescar();
  if (id === 'v-compilador') cargarProgramas();
  const first = view.querySelector('input, select');
  if (first) first.focus();
  window.scrollTo(0, 0);
}

document.addEventListener('click', (e) => {
  const b = e.target.closest('[data-go]');
  if (b) show(b.dataset.go);
});

// Envía un formulario deshabilitando su botón mientras espera.
async function enviar(form, fn) {
  const btn = form.querySelector('[type=submit]');
  const out = form.querySelector('.msg');
  btn.disabled = true;
  msg(out, '');
  try { await fn(out); } catch (err) { msg(out, err.message, false); } finally { btn.disabled = false; }
}

function entrar(c) {
  cuenta = c;
  store.set(c.telefono);
  show('v-inicio');
}

// ---- Ingreso / registro ----
$('#f-login').addEventListener('submit', (e) => {
  e.preventDefault();
  const tel = $('#login-tel').value.trim();
  enviar(e.target, async (out) => {
    if (!TEL.test(tel)) return msg(out, 'El celular debe tener 10 dígitos', false);
    entrar(await api(`/api/cuentas/${tel}`));
  });
});

$('#f-registro').addEventListener('submit', (e) => {
  e.preventDefault();
  const telefono = $('#reg-tel').value.trim();
  const nombre = $('#reg-nombre').value.trim();
  enviar(e.target, async (out) => {
    if (!TEL.test(telefono)) return msg(out, 'El celular debe tener 10 dígitos', false);
    if (!nombre) return msg(out, 'Escribe tu nombre', false);
    entrar(await api('/api/cuentas', { telefono, nombre }));
  });
});

$('#btn-salir').addEventListener('click', () => {
  cuenta = null;
  store.del();
  $('#f-login').reset();
  show('v-login');
});

// ---- Inicio ----
const TIPOS = {
  CONSIGNACION: { txt: 'Consignación', ico: 'arrow-down', entra: true },
  RETIRO: { txt: 'Retiro', ico: 'arrow-up', entra: false },
  TRANSFERENCIA_ENVIADA: { txt: 'Transferencia enviada', ico: 'send', entra: false },
  TRANSFERENCIA_RECIBIDA: { txt: 'Transferencia recibida', ico: 'arrow-down', entra: true },
};

function pintarCuenta() {
  $('#saludo').textContent = `Hola, ${cuenta.nombre}`;
  $('#saldo').textContent = cop.format(cuenta.saldo);
  $('#tel-actual').textContent = `Cel. ${cuenta.telefono}`;
}

function pintarMovs(movs) {
  const ul = $('#movs');
  ul.textContent = '';
  if (!movs.length) {
    const li = document.createElement('li');
    li.className = 'muted';
    li.textContent = 'Aún no tienes movimientos.';
    ul.append(li);
    return;
  }
  const frag = document.createDocumentFragment();
  for (const m of movs) {
    const t = TIPOS[m.tipo] || { txt: m.tipo, ico: 'history', entra: false };
    const dir = t.entra ? 'in' : 'out';
    const fecha = new Date(m.fecha);
    const detalle = [m.contraparte ? (t.entra ? 'De ' : 'A ') + m.contraparte : null,
      isNaN(fecha) ? m.fecha : fechaFmt.format(fecha)].filter(Boolean).join(' · ');
    const li = document.createElement('li');
    li.innerHTML =
      `<span class="mov-ico ${dir}"><svg class="ico" aria-hidden="true"><use href="#i-${t.ico}"/></svg></span>` +
      `<div class="mov-txt"><strong></strong><span></span></div>` +
      `<div class="mov-monto ${dir}"><b></b><span></span></div>`;
    li.querySelector('strong').textContent = t.txt;
    li.querySelector('.mov-txt span').textContent = detalle;
    li.querySelector('.mov-monto b').textContent = (t.entra ? '+' : '-') + cop.format(m.monto);
    li.querySelector('.mov-monto span').textContent = 'Saldo ' + cop.format(m.saldoResultante);
    frag.append(li);
  }
  ul.append(frag);
}

async function refrescar() {
  if (!cuenta) return show('v-login');
  pintarCuenta();
  try {
    const [c, movs] = await Promise.all([
      api(`/api/cuentas/${cuenta.telefono}`),
      api(`/api/cuentas/${cuenta.telefono}/movimientos`),
    ]);
    cuenta = c;
    pintarCuenta();
    pintarMovs(movs || []);
  } catch (err) {
    $('#movs').innerHTML = '';
    const li = document.createElement('li');
    li.className = 'msg err';
    li.textContent = err.message;
    $('#movs').append(li);
  }
}

// ---- Operaciones ----
document.querySelectorAll('form.op').forEach((form) => {
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const op = form.dataset.op;
    const monto = Number(form.elements.monto.value);
    const destino = form.elements.destino ? form.elements.destino.value.trim() : null;
    enviar(form, async (out) => {
      if (!Number.isFinite(monto) || monto <= 0) return msg(out, 'El monto debe ser mayor a 0', false);
      let c;
      if (op === 'transferir') {
        if (!TEL.test(destino)) return msg(out, 'El celular destino debe tener 10 dígitos', false);
        if (destino === cuenta.telefono) return msg(out, 'No puedes transferirte a ti mismo', false);
        c = await api('/api/transferencias', { origen: cuenta.telefono, destino, monto });
      } else {
        c = await api(`/api/cuentas/${cuenta.telefono}/${op}`, { monto });
      }
      cuenta = c;
      form.reset();
      msg(out, `Listo. Nuevo saldo: ${cop.format(c.saldo)}`, true);
      refrescar();
    });
  });
});

// ---- Compilador ----
const sel = $('#sel-prog');
let programasCargados = false;

async function cargarProgramas() {
  if (programasCargados) return;
  try {
    const progs = await api('/api/cobol');
    sel.textContent = '';
    for (const p of progs) sel.append(new Option(p, p));
    programasCargados = true;
    if (progs.length) cargarFuente(progs[0]);
  } catch (err) {
    msg($('#comp-msg'), err.message, false);
  }
}

async function cargarFuente(prog) {
  const out = $('#comp-msg');
  msg(out, 'Cargando...', true);
  try {
    const d = await api(`/api/cobol/${encodeURIComponent(prog)}`);
    $('#code-cobol').textContent = d.cobol || '';
    $('#code-java').textContent = d.java || '';
    msg(out, '');
  } catch (err) {
    msg(out, err.message, false);
  }
}

sel.addEventListener('change', () => cargarFuente(sel.value));

// ---- Arranque: recordar sesión ----
(async () => {
  const tel = store.get();
  if (!tel) return;
  try { entrar(await api(`/api/cuentas/${tel}`)); } catch { store.del(); }
})();
