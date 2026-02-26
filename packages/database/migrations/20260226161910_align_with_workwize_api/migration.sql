/*
  Warnings:

  - You are about to drop the column `currency` on the `assets` table. All the data in the column will be lost.
  - You are about to drop the column `purchasePrice` on the `assets` table. All the data in the column will be lost.
  - You are about to drop the column `serialNumber` on the `assets` table. All the data in the column will be lost.

*/
-- AlterTable
ALTER TABLE "assets" DROP COLUMN "currency",
DROP COLUMN "purchasePrice",
DROP COLUMN "serialNumber",
ADD COLUMN     "condition" TEXT,
ADD COLUMN     "externalReference" TEXT,
ADD COLUMN     "invoiceCurrency" TEXT,
ADD COLUMN     "invoicePrice" DECIMAL(65,30),
ADD COLUMN     "serialCode" TEXT,
ADD COLUMN     "tags" JSONB,
ADD COLUMN     "warehouseStatus" TEXT;

-- AlterTable
ALTER TABLE "employees" ADD COLUMN     "foreignId" TEXT,
ADD COLUMN     "isDeactivated" BOOLEAN NOT NULL DEFAULT false,
ADD COLUMN     "registrationStatus" TEXT,
ADD COLUMN     "team" TEXT,
ADD COLUMN     "userId" TEXT;

-- AlterTable
ALTER TABLE "offices" ADD COLUMN     "employerId" TEXT,
ADD COLUMN     "managerId" TEXT;

-- AlterTable
ALTER TABLE "orders" ADD COLUMN     "expressDelivery" BOOLEAN NOT NULL DEFAULT false,
ADD COLUMN     "poNumber" TEXT,
ADD COLUMN     "receiver" TEXT,
ADD COLUMN     "receiverType" TEXT,
ADD COLUMN     "shippingInfo" JSONB,
ADD COLUMN     "totalProducts" INTEGER;

-- AlterTable
ALTER TABLE "warehouses" ADD COLUMN     "warehouseProvider" TEXT;
