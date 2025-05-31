$("#run").on("click", () => tryCatch(run));

async function run() {
  await Excel.run(async (context) => {
    const sheet1 = context.workbook.worksheets.getItem("Sheet1");
    const range = sheet1.getUsedRange();
    const newSheet = context.workbook.worksheets.add("RevenueSummary");

    // Create a table for summarizing revenue
    const summaryTable = newSheet.tables.add("A1:B1", true);
    summaryTable.name = "RevenueSummaryTable";
    summaryTable.getHeaderRowRange().values = [["Product", "Total Revenue"]];

    // Group by Product and sum Revenue
    const productRevenue = {};
    const values = range.values;

    for (let i = 1; i < values.length; i++) {
      const product = values[i][5]; // Column F: Product
      const revenue = values[i][6]; // Column G: Revenue

      if (productRevenue[product]) {
        productRevenue[product] += revenue;
      } else {
        productRevenue[product] = revenue;
      }
    }

    const summaryData = Object.entries(productRevenue).map(([product, totalRevenue]) => [product, totalRevenue]);
    summaryTable.rows.add(null, summaryData);

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