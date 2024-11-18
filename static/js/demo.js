async function dashboard() {
  let = target = $('<div/>')
    .html('<h1>Dashboard</h1>')
    .css({width: '1100px', margin: '20px auto auto auto'})
    .appendTo(document.body)

  let tbl = $("<table/>").addClass('table').appendTo(target);
  let header = $("<tr>").appendTo(tbl);
  let data = await $.getJSON('static/json/viz/table.json')
  let cols = _.keys(data[0])
  for (let col of cols) {
    $('<td/>').css("font-weight", "Bold").text(col).appendTo(header);
  }
  _.forEach(data, d => {
    let row = $('<tr/>').appendTo(tbl);
    for (let col of cols) {
      $('<td/>').text(d[col]).appendTo(row);
    }
    row.append($('<button/>', {
      class: 'btn btn-primary ',
      text: 'Watch',
      click: async function() {
        window.history.pushState("", "", `/?demo=viz&pid=${d.pid}`);
        target.remove();
        initializeDemo()
      }
    }));
  })
}

async function initializeDemo() {
  let search = new URLSearchParams(location.search)
  console.log('initializeDemo', search.get('demo'));
  switch (search.get('demo')) {
    case 'viz':
      let pid = search.get('pid');
      let trials = await $.getJSON(`static/json/viz/${pid}.json`);
      startDemo(trials);
      break;
    case 'dashboard':

    default:
      dashboard()
  }
}


async function startDemo(trials) {

  let demo = {
    type: 'mouselab',
    bonus_rate: 0.002,
    click_colors: ['#979AB6'],
    show_legend: false,
    option_title: '100 Balls',
    option_labels: ['Blue','Green','Yellow','Red'],
    delay: 500,
    timeline: trials
  }

  return startExperiment({
    timeline: [demo],
    exclusions: {
      min_width: 800,
      min_height: 600
    },
  });
}
