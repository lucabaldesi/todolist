var state = 'OK';

function set_state(stat) {
	var bar = document.getElementById('status');
	bar.classList.remove('alert-success');
	bar.classList.remove('alert-warning');
	if (state == 'OK')
		bar.classList.add('alert-success');
	else
		bar.classList.add('alert-warning');
	var msg = document.getElementById('state_label');
	msg.textContent = stat;
}

function drop_target(ev) {
	var target = ev.target
	while (target &&
	       (target.id != 'todolist' &&
	        target.id != 'donelist' &&
	        target.id != 'trash')) {
		target = target.parentElement;
	}
	if (target)
		return target.id
	else
		return 'todolist';
}

function allowDrop(ev) {
	ev.preventDefault();
}

function drag(ev) {
	target = ev.target
	id = target.id;
	while (id === undefined || ! id.startsWith('task')) {
		target = target.parentElement;
		id = target.id;
	}
	ev.dataTransfer.setData("text", id);
}

function drop(ev) {
	ev.preventDefault();
	var data = ev.dataTransfer.getData("text");
	var task = document.getElementById(data);
	var target = drop_target(ev)

	var xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			fetch_tasks();
		}
	};
	if (target != 'trash') {
		if (task.done && target == 'todolist' ||
		    !task.done && target == 'donelist') {
			xhttp.open("GET", "/done/"+task.tid, true);
			xhttp.send();
			state = 'DOING';
			set_state("Moving " + task.id);
		}
	} else {
		xhttp.open("GET", "/delete/"+task.tid, true);
		xhttp.send();
		state = 'DOING';
		set_state("Deleting " + task.id);
	}
}

function create_task() {
	var xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			fetch_tasks();
		}
	};
	xhttp.open("POST", "/task", true);
	xhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
	cont = document.getElementById('content');
	if (cont.value != undefined) {
		params = 'content=' + encodeURIComponent(cont.value);
		xhttp.send(params);
		content.value='';
	}
}

function task_choc_menu(task_id, chocolate) {
	var choc = document.createElement("SELECT");
	choc.style = "float: right";
	choc.className="choc-select";
	choc.onchange = function () {
		var xhttp = new XMLHttpRequest();
		xhttp.onreadystatechange = function() {
			if (this.readyState == 4 && this.status == 200) {
				state = 'OK'
				set_state("Data synchronized");
				fetch_tasks();
			}
		};
		params = 'chocolate=' + encodeURIComponent(choc.value);
		xhttp.open("UPDATE", "/tasks/" +
		           encodeURIComponent(task_id) +
		           "?format=json", true);
		xhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
		xhttp.send(params);
		state = 'DOING'
		set_state("Changing chocolate amount");
	};

	for (var i=0; i<10; i++) {
		var opt = document.createElement("OPTION");
		opt.textContent = i;
		choc.appendChild(opt);
	}
	choc.value = chocolate;

	return choc
}

function update_tasks(tasks) {
	var todo = document.getElementById("todolist");
	var done = document.getElementById("donelist");
	while (todo.firstChild) {
		todo.removeChild(todo.firstChild);
	}
	while (done.firstChild) {
		done.removeChild(done.firstChild);
	}

	tasks.sort(function (a, b) {return b.chocolate - a.chocolate});
	for (i in tasks) {
		var node = document.createElement("LI");
		node.id = 'task'+tasks[i].id;
		node.tid = tasks[i].id;
		node.done = tasks[i].done;
		node.className="row center-block list-group-item text-center allselect";

		var textnode = document.createElement("SPAN");
		textnode.textContent = tasks[i].content;
		textnode.className="col-md-11";
		textnode.draggagle=true;
		textnode.ondragstart=drag;
		node.appendChild(textnode);
		node.appendChild(task_choc_menu(node.tid, tasks[i].chocolate));

		if (tasks[i].done)
			done.appendChild(node);
		else
			todo.appendChild(node);

		node.draggagle=true;
		node.ondragstart=drag;
	}
}

function fetch_tasks() {
	var xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			var tasks = JSON.parse(this.responseText);
			update_tasks(tasks);
			state = 'OK'
			set_state("Data synchronized");
		}
	};
	xhttp.open("GET", "/?format=json", true);
	xhttp.send();
}

document.addEventListener('DOMContentLoaded', function(event) {
	fetch_tasks();
})
