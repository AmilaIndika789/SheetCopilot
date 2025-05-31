$("#run").on("click", () => tryCatch(run));

async function run() {
  await Excel.run(async (context) => {
    const sheet1 = context.workbook.worksheets.getItem("Sheet1");
    const range = sheet1.getUsedRange();
    
    // Create a new worksheet for the pivot table
    const pivotSheet = context.workbook.worksheets.add("PivotTableSheet");
    
    // Create the pivot table
    const pivotTable = pivotSheet.pivotTables.add("RevenuePivotTable", range, "A1");
    pivotTable.rowHierarchies.add(pivotTable.hierarchies.getItem("Product"));
    pivotTable.dataHierarchies.add(pivotTable.hierarchies.getItem("Revenue ($)"), Excel.DataPivotSummaryFunction.sum);
    
    await context.sync();
    
    // Create a horizontal bar chart based on the pivot table
    const chart = pivotSheet.charts.add(Excel.ChartType.barClustered, pivotTable.getRange(), Excel.ChartSeriesBy.auto);
    chart.title.text = "Revenue of each product";
    chart.legend.setVisible(false);
    
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