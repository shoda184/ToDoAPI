const api = {
  list:   () => fetch('/todos/').then(r => r.json()),
  create: (title) => fetch('/todos/', {
              method: 'POST',
              headers: {'Content-Type': 'application/json'},
              body: JSON.stringify({ title, done: false })
           }).then(r => r.json()),
  update: (t) => fetch(`/todos/${t.id}`, {
              method: 'PUT',
              headers: {'Content-Type': 'application/json'},
              body: JSON.stringify(t)
           }).then(r => r.json()),
  del:    (id) => fetch(`/todos/${id}`, { method: 'DELETE' })
};

const $list = document.getElementById('list');

const render = (items = []) => {
  $list.innerHTML = '';
  items.forEach(t => {
    const li = document.createElement('li');
    const chk = document.createElement('input');
    chk.type = 'checkbox'; chk.checked = t.done;

    const span = document.createElement('span');
    span.textContent = t.title;
    span.className = t.done ? 'done' : '';

    const del = document.createElement('button');
    del.textContent = 'Delete';

    chk.onchange = async () => { t.done = chk.checked; await api.update(t); load(); };
    del.onclick = async () => { await api.del(t.id); load(); };

    li.append(chk, span, del);
    $list.append(li);
  });
};

async function load() { render(await api.list()); }

document.getElementById('add').onclick = async () => {
  const input = document.getElementById('title');
  const title = input.value.trim();
  if (!title) return;
  await api.create(title);
  input.value = '';
  load();
};

load();
