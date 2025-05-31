$("#run").on("click", () => tryCatch(run));

async function run() {
  await Excel.run(async (context) => {
    const sheet = context.workbook.worksheets.getItem("Sheet1");
    
    // Add a new column for Profit
    const profitColumn = sheet.getRange("D1");
    profitColumn.values = [["Profit"]];
    
    // Calculate Profit = Sales - COGS
    const salesRange = sheet.getRange("B2:B11");
    const cogsRange = sheet.getRange("C2:C11");
    const profitRange = sheet.getRange("D2:D11");
    
    profitRange.formulas = salesRange.formulas.map((row, index) => {
      return [[`=B${index + 2}-C${index + 2}`]];
    });

    // Create a chart for Sales, COGS, and Profit
    const chart = sheet.charts.add(Excel.ChartType.line, sheet.getRange("A1:D11"), Excel.ChartSeriesBy.columns);
    chart.title.text = "Weekly Sales, COGS, and Profits";
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