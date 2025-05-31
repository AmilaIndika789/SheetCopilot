$("#run").on("click", () => tryCatch(run));

async function run() {
  await Excel.run(async (context) => {
    const sheet1 = context.workbook.worksheets.getItem("Sheet1");
    const usedRange = sheet1.getUsedRange();
    usedRange.load("values");

    await context.sync();

    // Create a new sheet for the summary
    const sheet2 = context.workbook.worksheets.add("Weekly Revenue Summary");

    // Create a map to summarize revenue by week
    const revenueByWeek = new Map();

    // Summarize revenue by week
    for (let i = 1; i < usedRange.values.length; i++) {
      const week = usedRange.values[i][2]; // Week column
      const revenue = usedRange.values[i][6]; // Revenue column

      if (revenueByWeek.has(week)) {
        revenueByWeek.set(week, revenueByWeek.get(week) + revenue);
      } else {
        revenueByWeek.set(week, revenue);
      }
    }

    // Prepare data for the new sheet
    const summaryData = [["Week", "Total Revenue"]];
    revenueByWeek.forEach((value, key) => {
      summaryData.push([key, value]);
    });

    // Write summary data to the new sheet
    const summaryRange = sheet2.getRange("A1:B" + summaryData.length);
    summaryRange.values = summaryData;

    // Create a line chart based on the summary data
    const chart = sheet2.charts.add(Excel.ChartType.line, summaryRange, Excel.ChartSeriesBy.columns);
    chart.title.text = "Weekly Revenue Summary";
    chart.legend.position = Excel.ChartLegendPosition.bottom;

    await context.sync();
  });
}

/** Default helper for invoking an action and handling errors. */
async function tryCatch(callback) {
  try {
    await callback();
  } catch (error) {
    // Note: In a production add-in, you'd want to notify the user through your add-in's UI.
    console.error(error);
  }
}