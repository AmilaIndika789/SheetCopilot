$("#run").on("click", () => tryCatch(run));

async function run() {
  await Excel.run(async (context) => {
    const sheet1 = context.workbook.worksheets.getItem("Sheet1");
    const range = sheet1.getUsedRange();
    range.load("values");

    await context.sync();

    const salesData = range.values.slice(1); // Exclude header
    const avgSales = salesData.map(row => {
      const totalSales = row.slice(1).reduce((sum, value) => sum + (value || 0), 0);
      const avg = totalSales / (row.length - 1);
      return [row[0], avg]; // Sales Rep and Avg Sales
    });

    const newSheet = context.workbook.worksheets.add("Average Sales");
    const avgSalesTable = newSheet.tables.add("A1:B1", true);
    avgSalesTable.name = "AvgSalesTable";
    avgSalesTable.getHeaderRowRange().values = [["Sales Rep", "Avg Sales"]];
    avgSalesTable.rows.add(null, avgSales);

    newSheet.getUsedRange().format.autofitColumns();
    newSheet.getUsedRange().format.autofitRows();
    newSheet.activate();

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